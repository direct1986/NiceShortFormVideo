# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : models.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/6/15 1:33
--------------------------------------
"""
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, Float

from settings import cfg

# check_same_thread = False, 解决多线程报错的问题
engine = sqlalchemy.create_engine(cfg.db_uri, connect_args={"check_same_thread": False})
Base = declarative_base()


# 定义映射类User，其继承上一步创建的Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    createdOn = Column(DateTime, server_default=func.now(), comment='创建时间')
    updatedOn = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')  # 时间自动更新


class Videos(BaseModel):
    __tablename__ = "videosData"
    md5 = Column(String(32), index=True, comment='MD5值')
    size = Column(Float(1), comment='文件大小，MB')
    url = Column(String, index=True, comment='videos 地址')


def create_db():
    Base.metadata.create_all(engine)
