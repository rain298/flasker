# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetForm, PasswordResetRequestForm, ChangeEmailForm
from .. import db
from ..email import send_email


# 对蓝本来说， before_request 钩子只能应用到属于蓝本的请求上。若想在
# 蓝本中使用针对程序全局请求的钩子， 必须使用 before_app_request 修饰器。
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:     # 更新已登录用户的访问时间
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 当请求类型是 GET 时，视图函数直接渲染模板，即显示表单。
    if form.validate_on_submit():  # 当表单在 POST 请求中提交时，Flask-WTF 中的 validate_on_submit() 函数会验证表单数据，然后尝试登入用户。
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)  # 如果密码正确，则调用 Flask-Login 中的 login_user() 函数，在用户
            # 会话中把用户标记为已登录。login_user() 函数的参数是要登录的用户，以及可选的“记住我”布尔值，
            # “记住我”也在表单中填写。 “记住我”的功能只需要向 login_user 调用传递 remember=True 。一个 cookie
            # 就会存储在用户 的电脑上，且之后如果会话中没有用户 ID，Flask-Login 会自动从那个 cookie 上恢复用户 ID。
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'无效的用户名或密码.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')   # 退出路由
@login_required         # 需要用户登入的视图可以用 login_required 装饰器来装饰,作用是保护路由，只允许已登录用户访问。
def logout():
    logout_user()      # 这个视图函数调用 Flask-Login 中的 logout_user() 函数，这个函数的功能是删除并重设用户会话。
    flash(u'您已经退出登录.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, u'确认您的账户', 'auth/email/confirm', user=user, token=token)
        flash(u'一封确认电子邮件已发送到您的邮箱，请注意查收，有效期1小时，或许Ta在您的垃圾箱中～')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):               # 注册时候要确认邮箱，点击确认链接后，调用的路由
    if current_user.confirmed:    # 这个函数先检查已登录的用户是否已经确认过， 如果确认过，则重定向到首页，
        return redirect(url_for('main.index'))  # 这样处理可以避免用户不小心多次点击确认令牌带来的额外工作。
    if current_user.confirm(token):
        flash(u'您已确认账户。谢谢!')  # 确认成功后， User 模型中 confirmed 属性的
        # 值会被修改并添加到会话中，请求处理完后，这两个操作被提交到数据库。
    else:
        flash(u'确认链接已失效或过期。')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required       # 这个路由也用 login_required 保护，确保访问时程序知道请求再次发送邮件的是哪个用户。
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'确认您的账户',
               'auth/email/confirm', user=current_user, token=token)
    flash(u'一封确认邮件已发送至您的邮箱。')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(u'您的密码已更改。')
            return redirect(url_for('main.index'))
        else:
            flash(u'无效的密码')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'post'])
def password_reset_request():             # 重设密码的请求(忘记密码)
    if not current_user.is_anonymous:     # 防止已登录用户用这种方式修改密码(可以通过在浏览器直接输入地址)
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置您的密码', 'auth/email/reset_password',
                       user=user, token=token, next=request.args.get('next'))
            flash(u'一封重置密码提示已发送至您的邮箱。')
        else:
            flash(u'该账户不存在,请仔细核对邮箱。')
            return redirect(url_for('auth.password_reset_request'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):       # 从邮箱邮件链接点击之后，URL里的token在此处会用到
    if not current_user.is_anonymous:    # 点击邮箱里的重置密码链接，如果用户已经登录的话，则重定向到首页
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash(u'您的密码已被更改。')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():   # base.html页面点击更改邮箱时发送的请求，调用这个路由
    form = ChangeEmailForm()   # 这里有坑。。。表单邮箱为新邮箱。但密码仍为旧密码才可以发送邮件
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.new_email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '确认您的邮件地址', 'auth/email/change_email',
                       user=current_user, token=token)
            flash(u'一封重置邮箱指南已发送至您的邮箱。')
            return redirect(url_for('main.index'))
        else:
            flash(u'无效的邮箱或密码')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):   # 邮箱邮件里点击链接跳转到新页面来更改邮箱，链接的地址里有令牌
    if current_user.change_email(token):
        flash(u'您的邮箱地址已更改')
    else:
        flash(u'无效的请求。')
    return redirect(url_for('main.index'))
