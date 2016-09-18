# -*- coding: utf-8 -*-
import unittest
from flask import current_app
from app import create_app, db


# setUp() 和 tearDown() 方法分别在各测试前后运行，并且名字以 test_ 开头的函数都作为测试执行。
class BasicsTestCase(unittest.TestCase):
    def setUp(self):  # setUp() 方法尝试创建一个测试环境，类似于运行中的程序。
        self.app = create_app('testing')  # 首先，使用测试配置创建程序
        self.app_context = self.app.app_context()  # 然后激活上下文。这一步的作用是确保能在测试中使用 current_app，像普通请求一样。
        self.app_context.push()
        db.create_all()  # 然后创建一个全新的数据库， 以备不时之需。

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])