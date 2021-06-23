# -*- encoding: utf-8 -*-

"""
------------------------------------------
@File       : base_orm_utils.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2021/6/23 10:23
------------------------------------------
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import SingletonThreadPool

from settings import cfg


def get_engine():
    _engine = None
    if "sqlite" in cfg.db_uri.lower():
        _engine = create_engine(
            cfg.db_uri,
            poolclass=SingletonThreadPool,
            connect_args={'check_same_thread': False}
        )

    else:
        _engine = create_engine(
            cfg.db_uri,
            pool_size=cfg.pool_size,
            max_overflow=cfg.max_overflow,
            pool_timeout=cfg.pool_timeout,
            pool_recycle=cfg.pool_recycle
        )

    return _engine


engine = get_engine()

Base = declarative_base()
