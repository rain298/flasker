# -*- coding: utf-8 -*-
from flask import g
from functools import wraps
from .errors import forbidden


# 用来防止未授权用户创建新博客文章的修饰器
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden(u'权限不足')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
