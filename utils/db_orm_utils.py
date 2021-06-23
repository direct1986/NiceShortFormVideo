# -*- encoding: utf-8 -*-

"""
------------------------------------------
@File       : db_orm_utils.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2021/6/6 22:48
------------------------------------------
"""
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, scoped_session

from utils.models import Videos, engine


class DataBase:
    def __init__(self):
        # 统一使用同一个变量，便于维护
        self.tb_data = Videos
        self.tv_data_keys = ["id", "url", "md5", "size"]
        session_factory = sessionmaker(bind=engine)
        self.session_safe = scoped_session(session_factory)

    def __get_session(self):
        return self.session_safe()

    def get_next_id(self) -> int:
        """获取最大值"""
        session = self.__get_session()
        row = session.query(self.tb_data).order_by(self.tb_data.id.desc()).first()
        next_id = (row.id + 1) if row else 1

        session.close()
        return next_id

    def insert(self, **kwargs):
        """插入数据"""
        tb_data = self.tb_data()

        for k in self.tv_data_keys:
            if k in kwargs:
                v = kwargs.get(k)
                setattr(tb_data, k, v)

        session = self.__get_session()
        session.add(tb_data)
        session.commit()
        session.close()

    def update(self, row_id: int, size: float):
        """更新数据"""
        session = self.__get_session()
        row = session.query(self.tb_data).filter(self.tb_data.id == row_id).first()
        row.endOn = func.now()
        row.size = size
        session.commit()
        session.close()

    def has_data(self, md5_value: str) -> bool:
        """通过判断MD5值，确定视频是否存在"""
        session = self.__get_session()
        row = session.query(self.tb_data).filter(self.tb_data.md5 == md5_value).first()
        session.close()

        return True if row else False

    def has_url(self, url: str) -> bool:
        """视频链接是否存在"""
        session = self.__get_session()
        row = session.query(self.tb_data).filter(self.tb_data.url == url).first()
        session.close()

        return True if row else False

    def fetch_all_hash_value(self):
        session = self.__get_session()
        rows = session.query(self.tb_data).with_entities(self.tb_data.md5).all()
        session.close()

        return {x[0] for x in rows} or rows
