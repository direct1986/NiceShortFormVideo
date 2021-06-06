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
from random import uniform
from time import sleep

from sqlalchemy import func

from utils import Parser, DataBase, Const, log, create_db


def spider(base_url: str, save_dir: str, headers, agents, total: int):
    db = DataBase()
    next_id = db.get_next_id()

    parser = Parser(base_url, headers, agents)

    counter, existed_counter = (1, 1)

    info = ""
    while counter <= total:
        url = parser.gen_url()
        start_date = func.now()
        code, r_url, r_headers, resp = parser.get_html(url)

        # 如果得到正确的响应并且获取到正确的URL，就进行下一步验证
        # 注释掉的条件  and db.has_url(url)

        try:
            content = resp.content
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

        sleep(uniform(1, 2))


def check_dir(dir_path):
    """
    检测是否存在文件夹，不存在则创建
    """
    if not exists(dir_path):
        makedirs(dir_path)
        print(f"{dir_path}, created.")


def main():
    # TODO: [2020-06-20] 加上异步、并发和队列
    # TODO: [2021-06-04] 自动创建数据库，一键小白式运行

    # 创建数据库
    try:
        create_db()
    except Exception as err:
        log.error(err)

    save_dir = "videos"
    # base_url = "http://www.kuaidoushe.com/video.php"
    # base_url2 = "https://tvv.tw/xjj/kuaishou/video.php"
    base_url3 = "http://wmsp.cc/video.php?"  # 这个反爬虫，设置(1, 1.5)秒的随机sleep可解除

    headers = Const.headers.value
    agents = Const.all_agents.value

    log.info("Downloader: start")
    check_dir(save_dir)
    spider(base_url3, save_dir, headers, agents, 1000)
    log.info("Downloader: done")


if __name__ == '__main__':
    main()
