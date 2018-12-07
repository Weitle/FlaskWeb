import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# 定义认证蓝图
# 所有以 '/auth' 打头的请求都由 auth_blueprint 处理
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@auth_blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'select * from user where id = ?', (user_id,)
        ).fetchone()

# 新用户注册
@auth_blueprint.route('/register', methods=['GET', 'post'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None
        # 必须性验证
        if not username:
            error = 'Username is requried'
        elif not password:
            error = 'Password is required'
        elif db.execute(
            'select id from user where username = ?', (username,)
        ).fetchone() is not None:
            # 用户已存在
            error = 'User {} is already registered.'.format(username)

        # 注册用户
        if error is None:
            db.execute(
                'insert into user(username, password) values(?, ?)', (username, generate_password_hash(password))
            )
            db.commit()
            flash(u'注册成功，请登录系统！')
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
# 请求 /auth/login 由该视图处理
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None
        user = db.execute(
            'select * from user where username = ?', (username,)
        ).fetchone()
        
        if user is None:
            # 未查找到用户
            error = 'User not exists.'
        elif not check_password_hash(user['password'], password):
            # 用户验证错误
            error = 'Incorrect Password.'
        
        if error is None:
            # 登录成功
            session.clear()
            session['user_id'] = user['id']
            flash(u'登录成功！欢迎你，{}！'.format(user['username']))
            return redirect('index')
        flash(error)
    return render_template('auth/login.html')

# 注销退出系统
@auth_blueprint.route('/logout')
def logout():
    session.clear()
    flash(u'成功退出系统!')
    return redirect(url_for('auth.login'))
