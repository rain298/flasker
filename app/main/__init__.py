# -*- coding: utf-8 -*-
from flask import Blueprint

main = Blueprint('main', __name__)  # 接收两个参数，蓝本的名字和蓝本所在包或模块的名字

from . import views, errors
from ..models import Permission


# 为了避免每次调用render_template()时都多添加一个模板参数，所以把Permission类加入模板上下文。
# 上下文处理器能让变量在所有模板中全局可访问。         见P101
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)