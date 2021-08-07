# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : run.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/6/15 0:39
--------------------------------------
"""
from os import makedirs, remove
from os.path import exists, join as path_join
from random import choice, shuffle
from threading import Lock
from time import time

from utils import (
    Parser, DataBase, log, create_db, CloseableQueue, start_threads, stop_thread, cfg)

# 创建数据库
try:
    create_db()
except Exception as err:
    log.error(err)

# 一些全局变量
db = DataBase()
parser = Parser()
lock = Lock()

# 设置两个全局变量，减少对数据库的1~2查询访问
# 这个量比较小，如果量比较大的话，可以用redis做缓存
g_urls = db.fetch_all_urls()
g_md5 = db.fetch_all_hash()

# 保存视频文件的目录
save_dir = cfg.videos_dir

# 第几个处理完成，已经存在的个数，下载失败的个数
counter, existed_counter, bad_counter = (1, 0, 0)

# 本轮下载，视频文件保存时候的开始序号，用于保存用
next_id = db.get_next_id()


class ParserError(Exception):
    pass


def check_dir(dir_path):
    """
    检测是否存在文件夹，不存在则创建
    """
    if not exists(dir_path):
        makedirs(dir_path)
        log.info(f"{dir_path}, created.")


def url_parse(url):
    """
        解析给定链接，返回视频二进制对象
    """
    global counter
    global bad_counter

    result = False
    r_url = None
    try:
        code, r_url, r_headers, resp = parser.get_html(url)
        content = resp.content

        # 针对访问两次才能获得视频对象的情况
        if b'<?xml' in content:
            code, r_url, r_headers, resp = parser.get_html(content.decode())
            content = resp.content

            if b'<?xml' not in content and len(content) > 500:
                result = (r_url, content)

            else:
                raise ParserError("返回结果非视频文件")

        else:
            result = (r_url, content)

    except Exception:
        # 这里没有将error记录到日志中，因为错误的类型和内容已非常熟悉，可以忽略，多整体影响不大
        log.error(f"Bad | URL: [{url}]\n R_URL: {r_url}")

        # 进度
        percent = round(counter / cfg.download_number * 100, 1) if counter < cfg.download_number else 100.0
        info = f" NO.{counter} | {percent}%, bad. "
        log.info(info)

        # 因为parser出错，未传递任何数据给下游队列，所以，该url的处理在本函数内结束
        # 所以，出错的时候才 counter + 1

        with lock:
            counter += 1
            bad_counter += 1

    return result


def video_check(item):
    """
        检验视频对象是否满足保存要求
    """
    global counter
    global existed_counter
    global g_urls
    global g_md5

    with lock:
        r_url, content = item
        md5_v = parser.get_hash(content)

        if r_url in g_urls or md5_v in g_md5:
            # 进度
            percent = round(counter / cfg.download_number * 100, 3) if counter < cfg.download_number else 100.0
            info = f"[ NO.{counter} | {percent}%, existed. ]"

            # 这里的existed信息不是重要信息，只是作为进度，不用保存到log
            print(info)

            existed_counter += 1

            # 同理，这里说明该视频已经下载过，对该视频（或者说由上游url产生的视频）的处理到此结束，
            # 所以，这里 counter += 1
            counter += 1
            return

        return r_url, md5_v, content


def video_save(item):
    """
        保存视频对象为文件，并在数据库中添加相应的内容
    """
    global counter
    global next_id
    global g_urls
    global g_md5

    r_url, md5_v, content = item
    file_path = path_join(save_dir, f"{next_id}.mp4")

    # 保存文件
    parser.save(file_path, content)

    # 保存数据信息
    size = parser.get_size(file_path)

    # 如果大小小于0.5MB，删掉，很有可能是残次视频
    if size < 0.5:
        remove(file_path)

    data = {
        "id": next_id,
        "url": r_url,
        "md5": md5_v,
        "size": size
    }

    with lock:
        # 将新的url 或者 md5添加到全局变量中
        g_urls.add(r_url)
        g_md5.add(md5_v)

        try:
            db.insert(**data)
            # 进度
            percent = round(counter / cfg.download_number * 100, 3) if counter < cfg.download_number else 100.0
            info = f"NO.{counter} | {percent}% | file: {next_id}.m4 | saved."
            log.info(info)

        except Exception as save_err:
            log.error(f"NO.{counter} | url: {r_url} | err: {save_err}")

        next_id += 1
        counter += 1


def main():
    """
        todo:
            1. 使用redis做缓存对比
            2. 多线程下的 MySQL错误问题
            3. 内存爆炸问题
            4. 部分依然出错的网址的处理和再分析
            *5. 测试封装的DataBase对MySQL的ORM的通用性
        others:
            redis分布式锁：https://mp.weixin.qq.com/s/EBAe_UdAM0iXcFYhzm3KyA
    """
    # 开始时间
    start_time = time()

    # 检查保存视频的目录是否存在
    check_dir(save_dir)

    log.info("Downloader: start")

    queue_size = cfg.queue_size
    url_queue = CloseableQueue(queue_size)
    video_obj_queue = CloseableQueue(queue_size)
    video_save_queue = CloseableQueue(queue_size)
    done_queue = CloseableQueue(queue_size)

    url_parse_threads = start_threads(cfg.parser_worker, url_parse, url_queue, video_obj_queue)
    video_check_threads = start_threads(cfg.check_worker, video_check, video_obj_queue, video_save_queue)
    video_save_threads = start_threads(cfg.download_number, video_save, video_save_queue, done_queue)

    # 下载用的基础链接
    urls = cfg.urls

    # 向下载队列中填入生成的下载链接
    for _ in range(cfg.download_number):
        base_url = choice(urls)
        url_queue.put(parser.gen_url(base_url))

    stop_thread(url_queue, url_parse_threads)
    stop_thread(video_obj_queue, video_check_threads)
    stop_thread(video_save_queue, video_save_threads)

    # 下载统计
    # 下载的数量
    total = cfg.download_number
    saved_counter = cfg.download_number - existed_counter - bad_counter
    time_cost = round((time() - start_time) / 60 / 60, 2)

    report = f"""all work done
                    saved:   {saved_counter}\t[{round(saved_counter / total * 100, 1)}%]
                    existed: {existed_counter}\t[{round(existed_counter / total * 100, 1)}%]
                    bad:     {bad_counter}\t[{round(bad_counter / total * 100, 1)}%]
                    total:   {total}
                    time_cost: \t{time_cost} hour(s)\n"""
    log.info(report)


def download_with_url_from_file():
    """
        从文件中添加 url
    """
    # 去掉文件中已经下载过的url
    diff_urls_in_file()

    # 开始时间
    start_time = time()

    # 检查保存视频的目录是否存在
    check_dir(save_dir)

    log.info("Downloader with urls from file: start")

    queue_size = cfg.queue_size
    url_queue = CloseableQueue(queue_size)
    video_obj_queue = CloseableQueue(queue_size)
    video_save_queue = CloseableQueue(queue_size)
    done_queue = CloseableQueue(queue_size)

    url_parse_threads = start_threads(cfg.parser_worker, url_parse, url_queue, video_obj_queue)
    video_check_threads = start_threads(cfg.check_worker, video_check, video_obj_queue, video_save_queue)
    video_save_threads = start_threads(cfg.download_number, video_save, video_save_queue, done_queue)

    # 向下载队列中填入生成的下载链接
    file_path = "data/urls.txt"
    urls_from_file = parser.file_url_parser(file_path)
    shuffle(urls_from_file)  # 打乱原有顺序

    for i in urls_from_file:
        url_queue.put(i)

    stop_thread(url_queue, url_parse_threads)
    stop_thread(video_obj_queue, video_check_threads)
    stop_thread(video_save_queue, video_save_threads)

    # 下载统计
    # 下载的数量
    total = cfg.download_number
    saved_counter = cfg.download_number - existed_counter - bad_counter
    time_cost = round((time() - start_time) / 60 / 60, 2)

    report = f"""all work done
                        saved:   {saved_counter}\t[{round(saved_counter / total * 100, 1)}%]
                        existed: {existed_counter}\t[{round(existed_counter / total * 100, 1)}%]
                        bad:     {bad_counter}\t[{round(bad_counter / total * 100, 1)}%]
                        total:   {total}
                        time_cost: \t{time_cost} hour(s)\n"""
    log.info(report)


def diff_urls_in_file():
    """
        去掉文件中已经下载过的url
    """
    file_path = "data/urls.txt"
    urls = set()

    count = 1
    for url in parser.file_url_parser(file_path):
        urls.add(url)
        count += 1

    saved_urls = db.fetch_all_urls()
    diff_urls = urls - saved_urls

    log.info(f"old: {len(urls)} | new: {len(diff_urls)} | diff: {len(urls) - len(diff_urls)}")
    content = "\n".join(diff_urls)
    with open(file_path, 'w') as f:
        f.write(content)


def demo_test():
    file_path = "videos/10666.mp4"
    size = parser.get_size(file_path)
    print(f"{size} MB")


if __name__ == '__main__':
    # demo_test()
    # demo()
    # download_with_url_from_file()  # 用于解析从文件中读取的url
    # diff_urls_in_file()
    main()
