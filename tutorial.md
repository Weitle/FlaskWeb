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

