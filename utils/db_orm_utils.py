# -*- encoding: utf-8 -*-

"""
------------------------------------------
@File       : db_orm_utils.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2021/6/6 22:48
------------------------------------------
"""
from functools import wraps

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, scoped_session

from utils.models import Videos, engine


def session_manager(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        self.session = self.get_session()
        value = f(self, *args, **kwargs)
        self.session.close()

        return value

    return inner


class DataBase:
    def __init__(self):
        # 统一使用同一个变量，便于维护
        self.tb_data = Videos
        self.tv_data_keys = ["id", "url", "md5", "size"]
        session_factory = sessionmaker(bind=engine)
        self.session_safe = scoped_session(session_factory)
        self.session = None

    def get_session(self):
        return self.session_safe()

    @session_manager
    def get_next_id(self) -> int:
        """获取最大值"""
        row = self.session.query(self.tb_data).order_by(self.tb_data.id.desc()).first()
        next_id = (row.id + 1) if row else 1

        return next_id

    @session_manager
    def insert(self, **kwargs):
        """插入数据"""
        tb_data = self.tb_data()

        for k in self.tv_data_keys:
            if k in kwargs:
                v = kwargs.get(k)
                setattr(tb_data, k, v)

        self.session.add(tb_data)
        self.session.commit()

    @session_manager
    def update(self, row_id: int, size: float):
        """更新数据"""
        row = self.session.query(self.tb_data).filter(self.tb_data.id == row_id).first()
        row.endOn = func.now()
        row.size = size
        self.session.commit()

    @session_manager
    def has_data(self, md5_value: str) -> bool:
        """通过判断MD5值，确定视频是否存在"""
        row = self.session.query(self.tb_data).filter(self.tb_data.md5 == md5_value).first()

        return True if row else False

    @session_manager
    def has_url(self, url):
        """判断地址是否存在"""
        row = self.session.query(self.tb_data).filter(self.tb_data.url == url).first()

        return True if row else False

    @session_manager
    def has_url(self, url: str) -> bool:
        """视频链接是否存在"""
        row = self.session.query(self.tb_data).filter(self.tb_data.url == url).first()

        return True if row else False

    @session_manager
    def fetch_all_hash(self):
        rows = self.session.query(self.tb_data).with_entities(self.tb_data.md5).all()

        return {x[0] for x in rows} or rows

    @session_manager
    def fetch_all_urls(self):
        rows = self.session.query(self.tb_data).with_entities(self.tb_data.url).all()

        return {x[0] for x in rows} or rows
