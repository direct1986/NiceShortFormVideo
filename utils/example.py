# -*- encoding: utf-8 -*-

"""
------------------------------------------
@File       : example.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2021/6/17 11:11
------------------------------------------
使用案例：
    模拟照片 下载-调整大小-上传 的生产者消费者模式
"""
from time import sleep

from worker_queue_utils import stop_thread, CloseableQueue, start_threads


def download(d):
    sleep(1)
    result = f"{d}-d"
    print(result)

    return result


def resize(r):
    sleep(0.5)
    result = f"{r}-r"
    print(result)

    return result


def upload(u):
    sleep(0.5)
    result = f"{u}-u"
    print(result)

    return result


def main():
    download_queue = CloseableQueue()
    resize_queue = CloseableQueue()
    upload_queue = CloseableQueue()
    done_queue = CloseableQueue()

    download_threads = start_threads(3, download, download_queue, resize_queue)
    resize_threads = start_threads(4, resize, resize_queue, upload_queue)
    upload_threads = start_threads(5, upload, upload_queue, done_queue)

    for i in range(100):
        download_queue.put(i)

    stop_thread(download_queue, download_threads)
    stop_thread(resize_queue, resize_threads)
    stop_thread(upload_queue, upload_threads)

    print("完成：", done_queue.qsize())


if __name__ == '__main__':
    main()
