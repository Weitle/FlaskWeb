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

    from . import db
    db.init_app(app)

    # 返回 Flask 应用实例
    return app