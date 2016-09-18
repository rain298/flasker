# -*- coding:utf-8 -*-
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# 资料编辑表单
class EditProfileForm(Form):
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'家庭住址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'个人简介')
    submit = SubmitField(u'提交')


# 管理员使用的资料编辑表单
class EditProfileAdminForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(),
                                                   Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                      u'用户名只可以使用字母,数字，点或者下划线')])
    confirmed = BooleanField(u'认证状态')
    role = SelectField(u'职位', coerce=int)  # WTForms对HTML表单控件<select>进行SelectField包装，从而实现下拉列表，用来在这个表单中选择用户角色
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'家庭住址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'个人简介')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被使用.')


# 博客文章表单
class PostForm(Form):
    body = PageDownField(u"写下今天的心情吧！", validators=[DataRequired()])
    submit = SubmitField(u'提交')


# 评论输入表单
class CommentForm(Form):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField(u'提交')
