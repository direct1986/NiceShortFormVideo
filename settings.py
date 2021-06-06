# -*- encoding: utf-8 -*-

"""
------------------------------------------
@File       : settings.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2021/6/6 22:55
------------------------------------------
"""
from os.path import dirname, join as path_join


class BaseConfig:
    # 该文件所在的目录的绝对路径
    base_dir = dirname(__file__)

    # ORM格式的数据库地址
    db_uri = f"sqlite:///{base_dir}/kuaidou.db"

    # 日志配置
    log = {
        "log_dir": path_join(base_dir, "logs"),
        "filename": "belles_short_video.log"
    }


cfg = BaseConfig
