# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


# 登录表单 P83
class LoginForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])

    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u'下次直接登录')
    submit = SubmitField(u'登录')


# 用户注册表单 P88
class RegistrationForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(),Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                      u'用户名只可以使用字母,数字，点或者下划线')])
    password = PasswordField(u'密码', validators=[DataRequired(),
                                                     EqualTo('password2', message=u'您两次输入的密码不一致.')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被使用.')


# 仅仅是修改密码表单
class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[DataRequired()])
    password = PasswordField(u'新密码', validators=[
        DataRequired(), EqualTo('password2', message=u'您两次输入的密码不一致.')])
    password2 = PasswordField(u'确认新密码', validators=[DataRequired()])
    submit = SubmitField(u'确定')


# 忘记密码，重设密码请求时需要验证邮箱的表单
class PasswordResetRequestForm(Form):
    email = StringField(u'确认邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField(u'提交')


# 忘记密码，从邮箱里点击链接转到新页面时，重置密码的表单
class PasswordResetForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'新密码', validators=[
        DataRequired(), EqualTo('password2', message=u'您两次输入的密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'未知的电子邮箱.')


# 修改电子邮件地址, 转到新页面时要填新邮箱和密码表单
class ChangeEmailForm(Form):
    new_email = StringField(u'新邮箱', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField(u'旧密码', validators=[DataRequired()])
    submit = SubmitField(u'确定')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册.')
