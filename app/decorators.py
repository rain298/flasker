# -*- coding: utf-8 -*-
# 检查用户权限的两个自定义修饰器，作用是让视图函数只对具有特定权限的用户开房
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


# 用来检查常规权限
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):    # 如果用户不具有指定权限，则返回403错误代码，即HTTP"禁止"错误。
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# 专门用来检查管理员权限
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
