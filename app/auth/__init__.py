# -*- coding: utf-8 -*-
from flask import Blueprint

auth = Blueprint('auth', __name__)  # 接收两个参数，蓝本的名字和蓝本所在包或模块的名字

from . import views