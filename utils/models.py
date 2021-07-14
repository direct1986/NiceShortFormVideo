# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : models.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/6/15 1:33
--------------------------------------
"""
from sqlalchemy import Column, Integer, String, DateTime, func, Float

from .base_orm_utils import Base, engine


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    createdOn = Column(DateTime, server_default=func.now(), comment='创建时间')
    updatedOn = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')  # 时间自动更新


class Videos(BaseModel):
    __tablename__ = "videosData"
    md5 = Column(String(32), index=True, comment='MD5值')
    size = Column(Float(1), comment='文件大小，MB')
    url = Column(String(1536), index=True, comment='videos 地址')


def create_db():
    """
        创建数据库
    """
    Base.metadata.create_all(engine)
