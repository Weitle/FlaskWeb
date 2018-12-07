# Blueprint and View
- 视图 `view` 是应用对请求进行响应的函数，`flask` 通过路由匹配请求对应的处理视图，视图返回数据，`flask` 再把得到的数据作为响应返回请求端
## 创建蓝图
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

## 第一个视图：注册
