# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : downloader.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/6/15 0:39
--------------------------------------
"""
from hashlib import md5
from os import stat, makedirs
from os.path import exists
from random import random

import requests
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from models import engine, Videos


class DataBase:
    def __init__(self):
        # 统一使用同一个变量，便于维护
        self.tb_data = Videos
        self.tv_data_keys = ["id", "url", "md5", "size", "startOn", "endOn"]
        sess = sessionmaker(bind=engine)
        self.session = sess()

    def get_next_id(self) -> int:
        """获取最大值"""
        row = self.session.query(self.tb_data).order_by(self.tb_data.id.desc()).first()
        next_id = (row.id + 1) if row else 1

        return next_id

    def insert(self, **kwargs):
        """插入数据"""
        tb_data = self.tb_data()

        for k in self.tv_data_keys:
            if k in kwargs:
                v = kwargs.get(k)
                setattr(tb_data, k, v)

        self.session.add(tb_data)
        self.commit()

    def update(self, row_id: int, size: float):
        """更新数据"""
        row = self.session.query(self.tb_data).filter(self.tb_data.id == row_id).first()
        row.endOn = func.now()
        row.size = size
        self.commit()

    def has_data(self, md5_value: str) -> bool:
        """通过判断MD5值，确定视频是否存在"""
        row = self.session.query(self.tb_data).filter(self.tb_data.md5 == md5_value).first()

        return True if row else False

    def has_url(self, url: str) -> bool:
        """视频链接是否存在"""
        row = self.session.query(self.tb_data).filter(self.tb_data.url == url).first()
        return True if row else False

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()

    def __del__(self):
        self.close()


class Parser:
    """kaidouParser"""

    def __init__(self, base_url: str, headers: dict):
        self.base_url = base_url
        self.headers = headers

    def gen_url(self):
        t = random()
        url = f"{self.base_url}?_t={t}"

        return url

    def get_html(self, url: str) -> tuple:
        response = requests.request("GET", url, headers=self.headers)
        code = response.status_code
        url = response.url
        headers = response.headers

        return code, url, headers, response

    @staticmethod
    def get_hash(content: bytes) -> str:
        result = md5(content).hexdigest() if content else ""

        return result

    @staticmethod
    def get_size(arg: str or int or float) -> float:

        if isinstance(arg, str):
            kb = stat(arg).st_size
        else:
            kb = arg

        mb = round(kb / 1024 / 1024, 1)

        return mb

    @staticmethod
    def save(path, content):
        with open(path, "wb") as v:
            v.write(content)


def spider(base_url: str, headers: dict, save_dir: str, total: int):
    db = DataBase()
    next_id = db.get_next_id()

    parser = Parser(base_url, headers)

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
    save_dir = "videos"
    # base_url = "http://www.kuaidoushe.com/video.php"
    # base_url2 = "https://tvv.tw/xjj/kuaishou/video.php"
    base_url3 = "http://wmsp.cc/video.php?"  # 这个反爬虫

    headers = {'content-type': 'application/json',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

    print("[ Downloader: start ]")
    check_dir(save_dir)
    spider(base_url3, headers, save_dir, 1000)
    print("[ Downloader: done ]")


if __name__ == '__main__':
    main()
