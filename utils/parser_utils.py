# -*- encoding: utf-8 -*-

"""
------------------------------------------
@File       : parser_utils.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2021/6/6 22:31
------------------------------------------
"""
from hashlib import md5
from os import stat
from random import uniform
from time import time

import requests
from fake_headers import Headers


class Parser:
    """
        一些下载视频所用的通用方法
    """

    @staticmethod
    def gen_url(base_url):
        t = str(time()).replace(".", "")
        return f"{base_url}?_t=0.{t}"

    def get_html(self, url: str) -> tuple:
        response = requests.request("GET", url, headers=self.new_headers)
        code = response.status_code
        url = response.url
        headers = response.headers

        return code, url, headers, response

    @staticmethod
    def get_hash(content: bytes) -> str:
        result = md5(content).hexdigest() if content else ""

        return result

    @staticmethod
    def get_size(arg: str or int or float or bytes) -> float:
        """
        将给定的表示大小的值，转换为小数，单位转换为 MB
        """
        # 获取路径指向的文件的大小
        if isinstance(arg, str):
            kb = stat(arg).st_size

        # 获取传入的二进制对象的大小
        elif isinstance(arg, bytes):
            kb = len(arg) / 1024
        else:
            kb = arg

        mb = round(kb / 1024 / 1024, 1)

        return mb

    @staticmethod
    def save(path, content):
        """
         保存二进制为文件对象
        """

        with open(path, "wb") as v:
            v.write(content)

    @property
    def new_headers(self) -> dict:
        """随机生成 User-Agent, 并返回完整 headers"""

        return Headers(headers=True, browser='chrome').generate()
