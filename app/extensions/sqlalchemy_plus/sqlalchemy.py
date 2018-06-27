# -*- coding:utf-8 -*-
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy, BaseQuery, Model
import sqlalchemy as sa
from uuid import uuid1
from .schema import Paginator


def make_uuid():
    return str(uuid1()).replace('-', '').upper()


class CustomizedQuery(BaseQuery):

    def get_list(self, page=1, per_page=30):
        """
        这个方法是核心, 修正了SQLACHEMY的分页器, 把它变成了一个字典对象
        :param page: 第X页
        :param per_page: 每页多少项
        :return: 返回Paginator对象
        """
        page = page or 1
        per_page = per_page or 30
        return Paginator(self, page, per_page).render_page()


class IdModel(Model):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(32), default=make_uuid)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime, default=None)
    deleted = sa.Column(sa.Boolean, default=False)


class SQLAlchemyPlus(SQLAlchemy):
    pass
