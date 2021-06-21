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
from os.path import exists
from random import uniform, choice
from time import sleep

from fake_headers import Headers
from sqlalchemy import func

from utils import (
    Parser, DataBase, Const, log, create_db, CloseableQueue, StoppableWorker, start_threads, stop_thread, cfg)


def spider(base_url: str, save_dir: str, total: int):
    db = DataBase()
    next_id = db.get_next_id()

    parser = Parser()

    counter, existed_counter = (1, 1)

    info = ""
    while counter <= total:
        url = parser.gen_url(base_url)
        start_date = func.now()
        try:
            code, r_url, r_headers, resp = parser.get_html(url)
            # 如果得到正确的响应并且获取到正确的URL，就进行下一步验证
            # 注释掉的条件  and db.has_url(url)

            content = resp.content
            # 针对 base_url5 = "http://dou.plus/get/get1.php"的特点进行的优化
            if len(content) < 5000:
                code, r_url, r_headers, resp = parser.get_html(content.decode())
                content = resp.content
                if len(content) < 5000:
                    continue

            md5_v = parser.get_hash(content)

            if not db.has_data(md5_v):
                # 保存文件
                file_path = f"{save_dir}/{next_id}.mp4"
                parser.save(file_path, content)

                # 保存数据信息
                end_date = func.now()
                r_size = float(r_headers.get("content-length"))
                size = parser.get_size(r_size)

                if size == 0:
                    continue

                data = {
                    "id": next_id,
                    "url": r_url,
                    "md5": md5_v,
                    "size": size,
                    "startOn": start_date,
                    "endOn": end_date
                }
                db.insert(**data)
                d = {}

                # 进度
                percent = round(counter / total * 100, 1) if counter < total else 100.0
                info = f"[ NO.{counter} | {percent}% | file: {next_id}.m4 | saved. ]"
                next_id += 1

            else:
                info = f"[ NO.{counter} | MD5: {md5_v} | video existed. ]"
                existed_counter += 1

        except Exception as err:
            info = f"[ NO.{counter}, {err}. ]"

        print(info)
        counter += 1

        # sleep(uniform(2, 4))
        sleep(uniform(0, 2))


def check_dir(dir_path):
    """
    检测是否存在文件夹，不存在则创建
    """
    if not exists(dir_path):
        makedirs(dir_path)
        print(f"{dir_path}, created.")


def url_parse(url) -> str:
    """
        解析给定链接，返回视频链接
    """
    pass


def video_download(url) -> bytes:
    """
        解析给定的视频链接，返回视频二进制对象
    """
    pass


def video_save(video_object):
    """
        保存视频对象为文件
    """
    pass


def main():
    # 创建数据库
    try:
        create_db()
    except Exception as err:
        log.error(err)

    db = DataBase()
    save_dir = cfg.videos_dir
    check_dir(save_dir)

    parser = Parser()
    next_id = db.get_next_id()

    # 下载到第几个，已经存在的个数
    counter, existed_counter = (1, 1)

    log.info("Downloader: start")

    # spider(base_url5, save_dir, 1000)
    log.info("Downloader: done")

    url_queue = CloseableQueue()
    video_url_queue = CloseableQueue()
    video_obj_queue = CloseableQueue()
    done_queue = CloseableQueue()

    url_parse_threads = start_threads(3, url_parse, url_queue, video_url_queue)
    video_download_threads = start_threads(4, video_download, video_url_queue, video_obj_queue)
    video_save_threads = start_threads(5, video_save, video_obj_queue, done_queue)

    # 下载用的基础链接
    urls = cfg.urls

    # 向下载队列中填入生成的下载链接
    for _ in range(cfg.download_number):
        base_url = choice(urls)
        url_queue.put(parser.gen_url(base_url))

    stop_thread(url_queue, url_parse_threads)
    stop_thread(video_url_queue, video_download_threads)
    stop_thread(video_obj_queue, video_save_threads)

    print("完成：", done_queue.qsize())


def demo():
    # 新的 fake_headers用法
    for _ in range(3):
        headers = Headers(headers=True).generate()
        print(headers)
        print(type(headers))


if __name__ == '__main__':
    # main()
    demo()
