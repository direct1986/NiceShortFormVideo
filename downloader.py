# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : downloader.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/6/15 0:39
--------------------------------------
"""
from os import makedirs
from os.path import exists, join as path_join
from random import choice

from fake_headers import Headers

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
counter, existed_counter = (1, 0)

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
    code, r_url, r_headers, resp = parser.get_html(url)

    content = resp.content
    result = False

    # 针对访问两次才能获得视频对象的情况
    if len(content) < 5000:
        code, r_url, r_headers, resp = parser.get_html(content.decode())
        content = resp.content

        if len(content) > 5000:
            result = (r_url, content)

    else:
        result = (r_url, content)

    return result


def video_check(item):
    """
        检验视频对象是否满足保存要求
    """
    r_url, content = item
    md5_v = parser.get_hash(content)

    if db.has_data(md5_v):
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
    d = {}

    # 进度
    percent = round(counter / cfg.download_number * 100, 1) if counter < cfg.download_number else 100.0
    info = f"[ NO.{counter} | {percent}% | file: {next_id}.m4 | saved. ]"
    print(info)

    next_id += 1
    counter += 1


def main():
    # 检查保存视频的目录是否存在
    check_dir(save_dir)

    log.info("Downloader: start")
    log.info("Downloader: done")

    url_queue = CloseableQueue()
    video_obj_queue = CloseableQueue()
    video_save_queue = CloseableQueue()
    done_queue = CloseableQueue()

    url_parse_threads = start_threads(3, url_parse, url_queue, video_obj_queue)
    video_check_threads = start_threads(4, video_check, video_obj_queue, video_save_queue)
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

    print("完成：", done_queue.qsize())


def demo():
    # 新的 fake_headers用法
    for _ in range(3):
        headers = Headers(headers=True).generate()
        print(headers)
        print(type(headers))

    return


if __name__ == '__main__':
    main()
