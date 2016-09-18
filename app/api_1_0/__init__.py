# -*- coding: utf-8 -*-
from flask import Blueprint

api = Blueprint('api', __name__)  # 接收两个参数，蓝本的名字和蓝本所在包或模块的名字

from . import authentication, posts, users, comments, errors

