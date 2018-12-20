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

    # 注册数据库操作
    from . import db
    db.init_app(app)
    # 注册认证蓝图
    from . import auth
    #app.register_blueprint(auth.auth_blueprint)
    app.register_blueprint(auth.auth_blueprint, url_prefix='/auth')
    # 注册博客蓝图，并将 `blog.index` 视图关联到 `/` 路由
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    # 返回 Flask 应用实例
    return app