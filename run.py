# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : run.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/6/15 0:39
--------------------------------------
"""
from os import makedirs
from os.path import exists, join as path_join
from random import choice
from time import time, sleep

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

# 保存视频文件的目录
save_dir = cfg.videos_dir

# 下载到第几个，已经存在的个数
counter, existed_counter, bad_counter = (1, 0, 0)

# 本轮下载，视频文件保存时候的开始序号，用于保存用
next_id = db.get_next_id()


def check_dir(dir_path):
    """
    检测是否存在文件夹，不存在则创建
    """
    if not exists(dir_path):
        makedirs(dir_path)
        print(f"{dir_path}, created.")


def url_parse(url):
    """
        解析给定链接，返回视频二进制对象
    """

    result = False
    try:
        code, r_url, r_headers, resp = parser.get_html(url)
        content = resp.content

        # 针对访问两次才能获得视频对象的情况
        if len(content) < 5000:
            code, r_url, r_headers, resp = parser.get_html(content.decode())
            content = resp.content

            if len(content) > 5000:
                result = (r_url, content)

        else:
            result = (r_url, content)

    except Exception as parser_err:
        log.error(f"{url},{parser_err}")

        # 进度
        global counter
        global existed_counter
        global bad_counter

        percent = round(counter / cfg.download_number * 100, 1) if counter < cfg.download_number else 100.0
        info = f"[ NO.{counter} | {percent}%, bad. ]"
        print(info)

        counter += 1
        bad_counter += 1

    return result


def video_check(item):
    """
        检验视频对象是否满足保存要求
    """
    global counter
    global existed_counter

    r_url, content = item
    md5_v = parser.get_hash(content)

    if db.has_data(md5_v):
        # 进度
        percent = round(counter / cfg.download_number * 100, 1) if counter < cfg.download_number else 100.0
        info = f"[ NO.{counter} | {percent}%, existed. ]"
        print(info)

        existed_counter += 1
        counter += 1
        return

    return r_url, md5_v, content


def video_save(item):
    """
        保存视频对象为文件，并在数据库中添加相应的内容
    """
    global counter
    global next_id

    r_url, md5_v, content = item
    file_path = path_join(save_dir, f"{next_id}.mp4")

    parser.save(file_path, content)

    # 保存数据信息
    size = parser.get_size(content)

    data = {
        "id": next_id,
        "url": r_url,
        "md5": md5_v,
        "size": size
    }
    db.insert(**data)

    # 进度
    percent = round(counter / cfg.download_number * 100, 1) if counter < cfg.download_number else 100.0
    info = f"[ NO.{counter} | {percent}% | file: {next_id}.m4 | saved. ]"
    print(info)

    next_id += 1
    counter += 1


def main():
    # 开始时间
    start_time = time()

    # 检查保存视频的目录是否存在
    check_dir(save_dir)

    log.info("Downloader: start")

    url_queue = CloseableQueue()
    video_obj_queue = CloseableQueue()
    video_save_queue = CloseableQueue()
    done_queue = CloseableQueue()

    url_parse_threads = start_threads(2, url_parse, url_queue, video_obj_queue)
    video_check_threads = start_threads(2, video_check, video_obj_queue, video_save_queue)
    video_save_threads = start_threads(5, video_save, video_save_queue, done_queue)

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
                    total: {total}
                    saved: {saved_counter}\t{round(saved_counter / total * 100, 1)}%
                    existed: {existed_counter}\t{round(existed_counter / total * 100, 1)}%
                    bad: {bad_counter}\t{round(bad_counter / total * 100, 1)}%
                    time_cost: {time_cost} hour(s)"""
    log.info(report)


def demo():
    # 新的 fake_headers用法
    """
        bad :
            http://www.kuaidoushe.com/video.php?_t=0.29081044950531687
            https://xjj.349457.xyz/video.php?_t=0.03383993702189081
            https://xjj.349457.xyz/video.php?_t=0.8114063105460985
    """
    s = """
        b"<?xml version='1.0' encoding='utf-8' ?>\n<Error>\n\t<Code>NoSuchKey</Code>\n\t<Message>The specified key does not exist.</Message>\n\t<Resource>gifshowbak-10011997.cos.kwai-ap-beijing.myqcloud.com/upic/2020/09/17/23/BMjAyMDA5MTcyMzUwMjZfNjA4ODMzNzU2XzM2MjA0Nzk4MTE2XzBfMw==_b_B76dc109f4712d1296e8eeb414f1757f6.mp4</Resource>\n\t<RequestId>NjBkMzRhZTBfYTcwZWYyMDlfZTliMl8yNjQ4Njhm</RequestId>\n\t<TraceId>OGVmYzZiMmQzYjA2OWNhODk0NTRkMTBiOWVmMDAxODc0OWRkZjk0ZDM1NmI1M2E2MTRlY2MzZDhmNmI5MWI1OTQyYWVlY2QwZTk2MDVmZDQ3MmI2Y2I4ZmI5ZmM4ODFjZmFkYWRjYTUzYjBlOWY1NGE2ZjIyYzBiYjE2NmQwYmE=</TraceId>\n</Error>\n\n"
    """

    base_url = "http://www.kuaidoushe.com/video.php"
    for no in range(1, 11):
        url = parser.gen_url(base_url)
        code, r_url, r_headers, resp = parser.get_html(url)
        print(resp)
        print(resp.content)

        sleep(10)

    """
    b"The requested URL '/upic/2020/09/20/21/BMjAyMDA5MjAyMTUxMzlfNDgzMTQ0MjJfMzYzNzk2ODE2ODVfMV8z_b_Bc500db173bc1d09d7ddb3abe272988a5.mp4' was not found on this server.\n"
    """


if __name__ == '__main__':
    """
        TODO:
            2. 数据库类的装饰器的添加
            3. ORM类数据库连接池的抽象并建库
            4. 部分依然出错的网址的处理和再分析
    """
    # main()
    demo()
