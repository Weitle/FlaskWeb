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


    [上一章 Readme](README.md)

    [下一章 蓝图](blueprint.md)