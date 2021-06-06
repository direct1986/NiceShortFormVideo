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
from random import choice, random

import requests


class Parser:
    """
        一些下载视频所用的通用方法
    """

    def __init__(self, base_url: str, headers: dict, agents: list):
        self.base_url = base_url
        self.headers = headers
        self.agents = agents

    def gen_url(self):
        t = random()
        url = f"{self.base_url}?_t={t}"

        return url

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
    def get_size(arg: str or int or float) -> float:
        """
        将给定的表示大小的值，转换为小数，单位转换为 MB
        """
        if isinstance(arg, str):
            kb = stat(arg).st_size
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

        agent = choice(self.agents)
        self.headers.update({"User-Agent": agent})

        return self.headers
