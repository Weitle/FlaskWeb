import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# 定义认证蓝图
# 所有以 '/auth' 打头的请求都由 auth_blueprint 处理
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# 每个请求的开头，判断用户是否已经登录
# 如果用户已经登录，将用户信息存入 `g.user` 中，使其可以用于其他视图函数
@auth_blueprint.before_app_request
def load_logged_in_user():
    # 获取 `session` 中的 `user_id`，用以判断用户是否已登录
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'select * from user where id = ?', (user_id,)
        ).fetchone()

# 新用户注册
 # 关联 `/register` 路由和 `register` 视图函数，方式为 `GET` 和 `POST` 的 `/register` 请求均由 `register` 视图函数处理
@auth_blueprint.route('/register', methods=['GET', 'post'])
def register():
    # 用户提交表单时，`request.method` 为 `POST`
    if request.method == 'POST':
        # 获取表单数据
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None
        # 表单数据验证
        # 必须性验证：用户名和密码均不能为空
        if not username:
            error = 'Username is requried'
        elif not password:
            error = 'Password is required'
        elif db.execute(
            'select id from user where username = ?', (username,)       # 查询用户是否存在（用户唯一性验证）
        ).fetchone() is not None:
            # 用户已存在，不能再进行注册
            error = 'User {} is already registered.'.format(username)

        # 数据验证通过，进行用户注册操作
        if error is None:
            db.execute(
                'insert into user(username, password) values(?, ?)', (username, generate_password_hash(password))
            )
            db.commit()
            # 注册成功后重定向至登录页面
            flash(u'注册成功，请登录系统！')
            return redirect(url_for('auth.login'))
        flash(error)
    # GET 请求返回 `register` 注册表单
    # POST 请求数据验证不成功时也返回 `register` 注册表单
    return render_template('auth/register.html')

# 用户登录
# 关联 `/login` 和 'login' 视图函数，HTTP 请求方式为 `GET` 和 `POST`
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # 用户提交登录表单后，`request.method` 为 `POST`
    if request.method == 'POST':
        # 获取登录表单数据
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None
        # 查询用户，判断用户是否存在
        user = db.execute(
            'select * from user where username = ?', (username,)
        ).fetchone()
        
        if user is None:
            # 未查找到用户，用户不存在
            error = 'User not exists.'
        elif not check_password_hash(user['password'], password):
            # 用户密码验证错误
            error = 'Incorrect Password.'
        
        if error is None:
            # 用户名和密码验证通过，登录成功，将用户 id 存储到 session 中，重定向至系统首页
            session.clear()
            session['user_id'] = user['id']
            flash(u'登录成功！欢迎你，{}！'.format(user['username']))
            return redirect('index')
        flash(error)
    # GET 请求返回用户登录表单
    # POST 请求用户登录失败也返回登录表单
    return render_template('auth/login.html')

# 用户注销退出系统
# 关联 `/logout` 路由和 `logout` 视图
@auth_blueprint.route('/logout')
def logout():
    # 注销用户时将用户 `id` 从 `session` 中移除并重定向至登录页面
    session.clear()
    flash(u'成功退出系统!')
    return redirect(url_for('auth.login'))
