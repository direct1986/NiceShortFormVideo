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
from sqlalchemy.orm import declarative_base

from settings import cfg

engine = create_engine(
    cfg.db_uri,
    pool_size=cfg.pool_size,
    max_overflow=cfg.max_overflow,
    pool_timeout=cfg.pool_timeout,
    pool_recycle=cfg.pool_recycle,
    connect_args={"check_same_thread": False}  # 解决多线程报错的问题,sqlite专有
)

Base = declarative_base()
