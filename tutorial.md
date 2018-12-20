# 教程
- 使用此教程创建一个名为 `Flaskr` 的具备基本功能的博客应用
- 实现用户注册和登录功能
- 用户可以发布、编辑、删除自己的文章

## 项目基本布局
- `flaskr/` ，一个包含应用代码和文件的 `python` 包
- `tests/` ，一个包含测试模块的文件夹

## 应用设置
- 一个 `Flask` 应用就是一个 `Flask` 类的实例，应用的所有东西都会与这个实例注册
- 使用一个应用工厂函数来创建一个 `Flask` 实例，s偶有应用相关的配置、注册和其他设置都在函数内部完成

### 应用工厂
- `__init__.py` 文件中创建一个 `create_app()` 函数用于生成 `Flask` 实例
    ```
        import os
        from flask import Flask

        def create_app(test_config=None):
            # create and configure the app
            app = Flask(__name__, instance_relative_config=True)
            app.config.from_mapping(
                SECRET_KEY = b'\x82\xe0\x94\xa8}\xacu\x89r\xfbn\x83\x0fu\xe1\xebZ&\x18\xd6}\x84\xc4\x1d\x92\xf1@VV\xdc\x0e?',
                DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
            )

            if test_config is None:
                # load the instance config, if it exists, when not testing
                app.config.from_pyfile('config.py', silent=True)
            else:
                # load the testing config if passed in
                app.config.from_mapping(test_config)

            # ensure the instance folder exists
            try:
                os.makedirs(app.instance_path)
            except OSError:
                pass

            # a simple page that say hello
            @app.route('/hello')
            def hello():
                return '<h1>Hello, World!</h1>'
            # 返回 Flask 应用实例
            return app
    ```
1. `app = Flask(__name__, instance_relative_config=True)` 创建 `Flask` 实例
    - `instance_relateive_config=True` 告诉应用配置文件是相对于 `instance_path` 的相对路径
    - 实例文件夹 `instance_path` 用于存放本地数据,如密钥和数据库等，默认位于 `flaskr` 应用包外边的 `instance` 目录
2. `app.config.from_mapping()` 用于设置一个默认的配置
    - `SECRET_KEY` 被 `Flask` 和扩展用来保证数据安全
    - `DATABASE` 数据库相关配置，本应用使用 `SQLite` 数据库，这里设置数据库文件的存放位置
3. `os.makedirs()` 确保 `app.instance_path` 的存在

### 运行应用
- 设置 `FLASK_APP=flaskr` 和 `FLASK_ENV=development` 
- 使用 `flask run` 命令运行应用
- 访问 `http://localhost:5000/hello`
    !['flaskr_hello'](flaskr/static/images/flaskr_hello.png)

## 定义和操作数据库
- 使用 `SQLite3` 数据库存储用户和博客内容
### 连接数据库
- 服务端处理请求时，根据业务需求建立数据库连接，处理完成后关闭释放连接
    ```
        # flaskr/db.py
        # 数据库处理
        import sqlite3
        import click
        from flask import current_app, g

        # 获取数据库连接
        def get_db():
            if 'db' not in g:
                # 建立连接
                g.db = sqlite3.connect(
                    current_app.config['DATABASE'],
                    detect_types=sqlite3.PARSE_DECLTYPES
                )
                # 返回一行数据的操作
                g.db.row_factory = sqlite3.Row
            # 返回数据库连接
            return g.db
        
        # 释放数据库连接
        def close_db(err):
            db = g.pop('db', None)
            if db is not None:
                db.close()
    ```
- `current_app` 指向处理请求的当前应用
- `sqlite3.connect()` 建立数据库连接，该连接指向配置中 `DATABASE` 指定的文件
- `sqlite3.Row` 返回一个行对象，然后可以根据列名称操作数据
### 创建表 - 使用 SQL
- 创建两张表：`user` 表存储用户数据，`post` 表存储博客数据
    ```
        # flaskr/schema.sql
        drop table user if exists;
        drop table post if exists;

        create table user(
            id integer primary key autoincrement,
            username text unique not null,
            password text not null
        );

        create table post(
            id integer primary key autoincrement,
            author_id integer not null,
            created timestamp not null default current_timestamp,
            title text not null,
            body text not null,
            foreign key (author_id) references user (id)
        );
    ```
- 在数据库操作文件 `db.py` 文件中添加函数，用于执行 `SQL` 命令创建表
    ```
        # db.py
        import click
        from flask.cli import with_appcontext

        def init_db():
            db = get_db()
            with current_app.open_resource('schema.sql') as f:
                db.executescript(f.read().decode('utf8'))

        @click.command('init-db')
        @with_appcontext
        def init_db_command():
            """
                Clear the exists data and create new tables.
            """
            init_db()
            click.echo('Initialized the database.')
    ```
    - `click.command()` 定义一个 `init-db` 命令，调用 `init_db` 函数初始化数据库，并为用户显示一个成功的消息
### 在应用中注册
- `close_db` 和 `init_db_command` 函数需要在应用实例中注册
- 定义 `init_app()` 函数，将应用当做参数，在函数中进行注册
    ```
        # flaskr/db.py
        def init_app(app):
            app.teardown_appcontext(close_db)
            app.cli.add_command(init_db_command)
    ```
- `app.teardown_appcontext()` 告诉 `Flask` 在返回响应后进行清理时调用此函数
- `app.cli.add_command()` 添加一个可以与 `flask` 一起工作的命令
- 在创建应用函数中将 `db` 与 `app` 绑定
    ```
        from . import db
        db.init_app(app)
    ```
### 初始化数据库文件
- 执行 `flask init-db` 命令初始化数据库，在实例目录 `instance` 中生成的数据库文件 `flaskr.sqlite`

## Blueprint and View
- 视图 `view` 是应用对请求进行响应的函数，`flask` 通过路由匹配请求对应的处理视图，视图返回数据，`flask` 再把得到的数据作为响应返回请求端
### 创建蓝图
- `Blueprint` 把视图及其他代码直接注册到蓝图，然后再把蓝图注册到应用
- 在 `Flaskr` 应用中注册两个蓝图：一个用于认证，一个用于博客帖子管理
- 认证蓝图 `auth.py`，该蓝图将包括注册新用户、登录和注销等功能（视图）
    ```
        # flaskr/auth.py
        import functools

        from flask import (
            Blueprint, flash, g, redirect, render_template, request, session, url_for
        )
        from werkzeug.security import check_password_hash, generate_password_hash
        from flaskr.db import get_db

        # 定义认证蓝图
        auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
    ```
    - 创建了一个名为 `auth_blueprint` 的蓝图，所有 `url_prefix` 为 `/auth` 的请求都由该蓝图进行处理
 - 使用 `app.register_blueprint()` 方法将蓝图注册到应用
    ```
        # flaskr/__init__.py
        # 注册蓝图
        from . import auth
        app.register_blueprint(auth.auth_blueprint)
    ```

### 第一个视图：注册
- 当用户以 `GET` 方式请求 `/auth/register` 时，`register` 视图会返回一个用于填写注册内容的表单
- 当用户提交表单后，以`POST` 方式请求 `/auth/register`, `register` 视图会验证表单内容，并进行注册业务处理
- 如果注册失败会显示错误信息并返回注册页面
- 如果注册成功会重定向至登录页面
    ```
        # flaskr/auth.py
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
    ```
### 登录视图
- 当用户以 `GET` 方式请求 `/auth/login` 时，`login` 视图会返回一个用于填写登录内容的表单
- 当用户提交表单后，以`POST` 方式请求 `/auth/login`, `login` 视图会验证表单内容，并进行登录业务处理
- 如果登录失败会显示错误信息并返回登录页面
- 如果登录成功会重定向至系统首页
    ```
        # flaskr/auth.py
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
    ```
- 在用户登录功能中，如果用户登录成功，将用户 `id` 写入 `session`，可以被后续请求使用
- 添加一个 `before_app_request` 装饰器，每次请求执行之前判断用户是否已登录，若用户已登录，查询用户信息并加载到 `g.user` 变量中
    ```
        # flaskr/auth.py
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
    ```
### 用户注销视图
- 以 `GET` 方式请求 `/auth/logout` 时，`logout` 视图进行注销用户
- 注销时会将 `user_id` 从 `session` 中移除，然后每次请求执行前查询用户登录状态都是未登录，不会添加用户信息到 `g.user` 中
    ```
        # flaskr/auth.py
        # 用户注销退出系统
        # 关联 `/logout` 路由和 `logout` 视图
        @auth_blueprint.route('/logout')
        def logout():
            # 注销用户时将用户 `id` 从 `session` 中移除并重定向至登录页面
            session.clear()
            flash(u'成功退出系统!')
            return redirect(url_for('auth.login'))
    ```
### 在其他视图中验证
- 用户只有在登录系统后才能具备创建、编辑和删除博客的权限
- 在每个视图中可以使用装饰器来完成这个工作
    ```
        flaskr/auth.py
        # 定义一个用户登录检测装饰器
        def login_required(view):
            @functools.wraps(view)
            def wrapped_view(**kwargs):
                # 如果用户没有登录，重定向至登录页面
                if g.user is None:
                    return redirect(url_for('auth.login'))
                # 用户移动能力，执行原视图
                return view(**kwargs)
            return wrapped_view
    ```
### 端点和 URL
- `flask.url_for()` 函数会根据视图名称生成对应的 `URL`
- 视图关联的名称称为端点，一般建议端点名称与视图函数名称一致
- 使用蓝图时，蓝图名称会添加到函数名称前面，如 `auth.py` 模块中的 `login` 视图对应的端点为 `auth.login`

## 模板
- 模板是包含静态数据和动态数据占位符的文件，视图会将数据传送给模板文件，模板文件利用这些数据生成最终的 `HTML` 文档
- `Flask` 使用 `Jinja` 模板
- 模板文件默认存储在包内的 `templates()` 目录下，视图函数通过调用 `render_template()` 函数调用模板文件
- 模板基本语法：
    - 代码块使用分界符分割
    - `{{` 和 `}}` 分界符之间会渲染其中的变量内容输出到最终文档
    - `{%` 和 `%}` 分界符之间表示流程控制语句
### 基础布局
- 为整个应用定制一个基本布局模板，其它模板可以继承这个基本布局模板并重载响应的 `block`，达到重用的效果
    ```
        # flaskr/templates/base.html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="ie=edge">
            <title>{% block title %}{% endblock %} - Flaskr</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"/>
        </head>
        <body>
        <nav>
            <h1>Flaskr</h1>
            <ul>
                {% if g.user %}
                    <li><span>{{ g.user['username'] }}</span></li>
                    <li><a href="{{ url_for('auth.logout') }}">Log Out</a></li>
                {% else %}
                    <li><a href="{{ url_for('auth.register' )}}">Register</a></li>
                    <li><a href="{{ url_for('auth.login') }}">Log In</a></li>
                {% endif %}
            </ul>
        </nav>
        <section class="content">
            <header>
                {% block header%}
                {% endblock %}
            </header>
            {% for message in get_flashed_messages() %}
                <div class="flash">{{ message }}</div>
            {% endfor %}
            {% block content %}{% endblock %}
        </section>
        </body>
        </html>
    ```
- 基础布局模板中定义了三个 `block`，可以被其它模板重载：
    1. `{% block title %}`：显示在浏览器标签的标题
    2. `{% block header %}`：显示页面标题
    3. `{% block content %}`：显示每个页面的具体内容
- 所有模板文件放在 `flaskr` 包下的 `templates` 目录下，属于某个蓝图的模板文件放在 `templates` 下与蓝图同名的目录下
### 注册
- 用于显示注册页面
- 使用 `{% extends 'base.html' %}` 表明本模板基于基础布局模板
    ```
        # flaskr/templates/auth/register.html
        {% extends 'base.html' %}

        {% block header %}
            <h1>{% block title %}Register{% endblock %}</h1>
        {% endblock %}

        {% block content %}
            <form method="POST">
                <label for="username">Username</label>
                <input type="text" name="username" id="username" required/>
                <label for="password">Password</label>
                <input type="password" name="password" id="password" required/>
                <input type="submit" value="Register"/>
            </form>
        {% endblock %}
    ```
### 登录
- 用于显示登录页面
    ```
        # flaskr/templates/auth/login.html
        {% extends 'base.html' %}

        {% block header %}
            <h1>{% block title %}Log In{% endblock %}</h1>
        {% endblock %}

        {% block content %}
            <form method="POST">
                <label for="username">Username</label>
                <input type="text" name="username" id="username" required/>
                <label for="password">Password</label>
                <input type="password" name="password" id="password" required/>
                <input type="submit" value="Log In"/>
            </form>
        {% endblock %}
    ```
## 静态文件
- `Flask` 会自动添加一个 `static` 视图，使用相对于 `flaskr/static` 相对路径。
- `CSS` 文件、`js` 文件、图片等都可以放在 `static` 目录中
- 使用 `url_for('static', filename='...')` 来引用静态文件
## 博客蓝图
 - 博客页面应该能够显示所有帖子，允许已登录用户创建帖子，允许帖子作者修改和删除帖子
 ### 定义并注册蓝图
 - 博客是 `Flaskr` 应用的主要功能，`blog` 蓝图不设置 `url_prefix`，但 `blog.py` 中的视图端点都会添加 `blog` 前缀
 - 使用 `add_url_rule()` 方法关联端点 `index`（`blog.index`）与 `/` 路由，这样使用 `url_for('index')` 和 `url_for('blog.index')` 都会生成 `/` 路由
    ```
        # flaskr/blog.py
        # 定义博客蓝图
        from flask import Blueprint

        bp = Blueprint('blog', __name__)
    ```
    ```
        #flaskr/__init__.py
        # 注册博客蓝图，并将 `blog.index` 视图关联到 `/` 路由
        from . import blog
        app.register_blueprint(blog.bp)
        app.add_url_rule('/', endpoint='index')
    ```
### 索引
- 博客的索引视图 `index` 用来显示所有帖子，并按照发表时间排序
- 为了显示用户信息，使用联合查询
    ```
        # flaskr/blog.py
        from flaskr.db import get_db
        from flask import render_template
        @bp.route('/')
        def index():
            db = get_db()
            posts = db.execute(
                'select p.id, title, body, created, author_id, username'
                ' from post p join user u on p.author_id = u.id'
                ' order by created desc'
            ).fetchall()
            return render_template('blog/index.html', posts = posts)
    ```
- 通过数据库查询出所有帖子，然后使用查询结果渲染 `blog/index.html` 模板
    ```
        # flaskr/templates/blog/index.html
        {% extends 'base.html' %}
        {% block header %}
            <h1>{% block title %}Posts{% endblock %}</h1>
            {% if g.user %}
                <a href="{{url_for('blog.create')}}" class="action">New</a>
            {% endif %}
        {% endblock %}
        {% block content %}
            {% for post in posts %}
                <article class="post">
                    <header>
                        <div>
                            <h1>{{ post['title'] }}</h1>
                            <div class="about"> by {{ post['username'] }} on {{ post['created'].strftime('%Y-%m-%d') }}</div>
                        </div>
                        {% if g.user['id'] == post['author_id'] %}
                            <a href="{{ url_for('blog.update', id=post['id']) }}" class="action">Edit</a>
                        {% endif %}
                    </header>
                    <p class="body">{{ post['body'] }}</p>
                </article>
                {% if not loop.last %}
                    <hr>
                {%endif%}
            {% endfor %}
        {% endblock %}
    ```
- `blog.index` 页面会显示所有帖子信息，如果是登录用户，会添加一个创建帖子的 `New` 链接，如果登录用户是某条帖子的作者，在该条帖子后添加一个编辑 `Edit` 链接
### 创建
- `create` 视图会渲染 `blog/create` 页面，显示一个表单，用于填写创建新的帖子的内容
- 对 `create` 视图应用 `login_required` 装饰器，用户必须登录后才能访问 `create` 视图，否则重定向至登录页面
    ```
        # flaskr/blog.py
        from .auth import login_required
        from flask import require, flash, url_for, redirect
        @bp.route('/create', methods=['GET', 'POST'])
        @login_required
        def create():
            if request.method == 'POST':
                title = request.form['title'].strip()
                body = request.form['body'].strip()
                error = None
                if not title:
                    error = 'Title is required.'
                if error is not None:
                    flash(error)
                else:
                    db = get_db()
                    db.execute("insert into post(title, body, author_id) values (?, ?, ?)", (title, body, g.user['id']))
                    db.commit()
                return redirect(url_for('blog.index'))
            return render_template('blog/create.html')
    ```
    ```
        # flaskr/templates/blog/create.html
        {% extends 'base.html' %}
        {% block header %}
            <h1>{% block title%}New Post{% endblock %}</h1>
        {% endblock %}
        {% block content %}
            <form action="{{url_for('blog.create')}}" method="post">
                <label for="title">Title</label>
                <input type="text" name="title" id="title" required>
                <label for="body">Body</label>
                <textarea name="body" id="body"></textarea>
                <input type="submit" value="Save"/>
            </form>
        {% endblock %}
    ```
### 更新
- 更新和删除都需要通过给定的 `id` 获取 `post`，并且验证登录用户是否是获取到的帖子的作者（是否具有更新和删除的权限）
- 定义一个 `get_post` 函数，用于实现获取 `post` 并验证用户的功能
    ```
        # flaskr/blog.py
        from flask import g, abort
        def get_post(id, check_author=True):
            db = get_db()
            post = db.execute("select p.id, title, body, created, author_id, username from post p join user u on p.author_id = u.id where p.id = ?", (id,)).fetchone()
            if post is None:
                abort(404, "Post id {0} doesn't exist.".format(id))
            # 检查登录用户是否有修改该帖子的权限
            if check_author and post['author_id'] != g.user['id']:
                abort(403)
            return post
    ```
- `blog.update` 视图接收一个 `id` 参数用于指定 `post.id`，该视图关联的路由格式为 `/<int:id>/update`，调用 `url_for` 生成 `URL` 时采用这样的方式：`url_for('blog.update', id=post['id'])`
    ```
        # flaskr/blog.py

        @bp.route('/<int:id>/update', methods=['GET', 'POST'])
        @login_required
        def update(id):
            # 根据给定的 id 获取相应的 post
            post = get_post(id)
            if request.method == 'POST':
                title = request.form['title'].strip()
                body = request.form['body'].strip()
                error = None
                if not title:
                    error = 'Title is required.'
                if error is not None:
                    flash(error)
                else:
                    db = get_db()
                    db.execute('update post set title = ?, body = ? where id = ?', (title, body, id))
                    db.commit()
                    return redirect(url_for('blog.index'))
            return render_template('blog/update.html', post=post)
    ```
    ```
        # flaskr/templates/blog/update.html
        {% extends 'base.html' %}
        {% block header %}
            <h1>{% block title%}Edit "{{post['title']}}"{% endblock %}</h1>
        {% endblock %}
        {% block content %}
            <form action="{{url_for('blog.update', id=post['id'])}}" method="post">
                <label for="title">Title</label>
                <input type="text" name="title" id="title" value="{{ request.form['title'] or post['title']}}" required>
                <label for="body">Body</label>
                <textarea name="body" id="body">{{ request.form['body'] or post['body'] }}</textarea>
                <input type="submit" value="Save"/>
            </form>
            <hr/>
            <form action="{{ url_for('blog.delete', id=post['id'] )}}" method="POST">
                <input type="submit" class="danger" value="Delete" onclick="return confirm('Are you sure?');"/>
            </form>
        {% endblock %}
    ```
### 删除
- 应用程序没有为 `delete` 视图提供模板，而是在 `blog/update` 模板中添加了一个 `delete` 链接按钮，指向 `/<int:id>/delete` 路由
    ```
        # flaskr/blog.py
        @bp.route('/<int:id>/delete', methods=('POST',))
        @login_required
        def delete(id):
            get_post(id)
            db = get_db()
            db.execute('delete from post where id = ?', (id,))
            db.commit()
            return redirect(url_for('blog.index'))
    ```
