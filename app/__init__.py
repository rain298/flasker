# -*- coding:utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'      # session_protection属性可以设置None, basic, strong,
# 设置为strong的时候Flask-Login 会监控用户的IP地址变动并提示用户重新登陆。 P82
login_manager.login_view = 'auth.login'        # login_view属性设置登录页面的端点。    P82


def create_app(config_name):  # 工厂函数，接收程序使用的配置名作为参数
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # 通过app.config配置对象的form_object方法直接导入配置
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
    config[config_name].init_app(app)  # 初始化配置

    bootstrap.init_app(app)  # 初始化
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app