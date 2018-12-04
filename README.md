# Flask Web Development
- Flask Web 开发学习笔记
- 使用 Python 3.7 和 Flask 1.0.2
- 使用 Anaconda 生成名为 `flask1.0` 的虚拟环境
    ```
        conda create -n flask1.0 python=3.7
    ```

## 安装 Flask 1.0.2
```
    pip install flask==1.0.2
```
- 自动安装以下包：
    - Jinja2-2.10
    - MarkupSafe-1.1.0
    - Werzeug-0.14.1
    - click-7.0
    - flask-1.0.2
    - itsdangerous-1.1.0

# 快速上手
## 一个最小的应用
- 创建一个 `hello.py` 文件
```
    from flask import Flask

    # 创建 Flask 类实例
    app = Flask(__name__)

    # 定义路由，当浏览器请求定义的路由时触发响应的函数
    # 定义 '/' 路由
    @app.route('/')
    def index():
        return "<h1>Home Page</h1>"
    # 定义 '/hello' 路由
    @app.route('/hello')
    def hello():
        return "<h1>Hello Flask!</h1>"
```

- 运行应用
    - 运行应用前首先定义环境变量 `FLASK_APP`
        - Linux 系统下使用
        ```
            export FLASK_APP=hello.py  
        ```
        - Windows 系统下使用
        ```
            set FLASK_APP=hello.py  
        ```
    - 运行应用
        ```
            flask run
        ```
        - 此时应用默认运行在 `127.0.0.1(localhost)` 的 `5000` 端口，这时只有自己的机器可以访问服务，而网络中的其他客户端无法访问服务
        - 可以通过设置 `--host` 参数为 `0.0.0.0` 让服务器可以被公开访问，设置 `--port` 参数设置服务运行的端口
            ```
                flask run --host 0.0.0.0 --port 8080
            ```
        - 调试模式：
            - 可以在服务器运行之前设置环境变量 `FLASK_ENV=development`
            - 也可以在应用中配置 `FLASK_DEBUG=1`
            - 不要在生产环境中启动调试模式

## 路由
- 使用 `route()` 装饰器把函数绑定到路由上
- 可以设置动态路由
### 路由变量规则
- 通过 URL 的一部分标记为 `<variable_name>` 就可以在 URL 中添加变量，标记的部分会作为关键字参数传递给函数
    ```
        @app.route('/user/<username>')
        def user(username):
            return "<h1>User %s</h1>" % username
    ```
- 还可以通过 `<converter:variable_name>` 为标记设置转换类型，可设置的类型有：`string, int, float, path, uuid`
    ```
        @app.route('/post/<int:postid>')
        def post(postid):
            return "<h1>Post #%d</h1>" % postid
    ```
### url_for() 函数
- `url_for()` 函数用于构建指定函数的 `URL`，函数名称作为第一个参数，还可以接受任意个关键字参数，每个关键字参数对应 `URL` 中的变量，未知变量将添加到 `URL` 中作为查询参数。
- 以目前已定义的路由为例：
    - `url_for('index')` 返回 `/` 路由
    - `url_for('user', username='weitle')` 返回 `/user/weitle` 路由
    - `url_fpr('hello', next='flask')` 返回 `/hello?next=flask` 路由
### HTTP 方法
- `Flask` 应用服务器会根据请求的 `HTTP` 方法j进行相应的处理，在 `route` 装饰器的 `method` 参数定义函数对应的请求方法，默认处理 `GET` 请求。
- 在业务处理函数中通过 `request` 对象的 `method` 方法来判断请求的方法。
    ```
        from flask import request

        # 定义 /login 路由，可以处理 GET 请求和 POST 请求
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username'].strip()
                return '<h1>Hello, %s!</h1>' % username
            content = """
                <form action='/login' method='POST'>
                    <b>Username</b> <input type='text' name='username' id='username'/><br/>
                    <input type='submit' value='Submit'/>
                </form>
            """
            return content
    ```
## 静态文件
- 静态文件默认放在包内或者模块旁边的 `static` 目录中
- 通过设置 `url_for()` 函数的第一个参数为 `static` 来生成静态文件对应的 `URL`
    - `url_for('static', filename='styles/test.css')` 对应的静态文件为 `static/styles/test.css`
## 使用模板
- `Flask` 默认使用 `Jinja2` 模板引擎
- 使用 `render_template()` 方法渲染模板，只要将模板名称和相应的参数传递给方法即可
- `Flask` 会在包内或者模块旁边的 `template` 目录下查找模板文件
- 一个简单例子
    - 当客户端请求 `/hello` 路由时，服务端会去 `templates` 目录下查找 `hello.html` 模板，并将 `name` 传递给模板文件渲染之后返回客户端
        ```
            from flask import render_template

            # 定义 '/hello' 路由， 使用 render_template() 方法渲染模板
            @app.route('/hello')
            @app.route('/hello/<name>')
            def hello(name=None):
                return render_template('hello.html', name = name)
        ```
    - 对应的模板文件 `templates/hello.html`
        ```
            {% if name %}
                <h1>Hello, {{ name }}!</h1>
            {% else %}
                <h1>Hello, Flask!</h1>
            {% end %}
        ```
    - 访问 `/hello/Weitle` 路由
        !['hello_Weitle'](static/images/hello_Weitle.png)
    - 访问 `/hello` 路由
        !['hello'](static/images/hello.png)
## 请求数据
### request 对象常见操作
- 前面 `hello()` 中已使用过 `request` 对象，下面以 `hello()` 方法为例
- 首先要从 `flask` 模块导入 `request` 对象
    ```
        from flask import request
    ```
- 通过使用 `method` 属性可以操作当前请求方法
    ```
        if request.method == 'POST':         # 判断当前请求是否是 POST 请求
    ```
- 通过使用 `form` 属性可以操作表单提交数据
    ```
        username = request.form['username']     # 获取表单提交的 username
    ```
    - 当 `form` 属性中不存在某个键时，会触发一个 `KeyError` 错误
- 通过使用 `args` 属性来获取 `URL` 中提交的参数
    ```
        id = request.args.get('id')     # 获取 URL 中 ?id=xxx 部分数据
    ```
### Cookies
- 通过 `request` 对象的 `cookies` 属性访问 `cookies`，该属性是一个字典，包含了客户端传输的所有 `cookies`
- 通过响应对象 `response` 的 `set_cookie()` 方法设置 `cookies`
- 建议使用会话 `session` ，而不是直接使用 `cookies`
## 会话
- `session` 对象允许在不同的请求之间储存信息
- 使用会话之前必须设置一个密钥，可以通过 `os.urandom()` 方法生成一个随机序列，通过 `app.config['SECRET_KEY']` 设置密钥
- 示例：
    ```
        from flask import session, redirect, url_for
        # 配置密钥
        app.config['SECRET_KEY'] = b'\x82\xe0\x94\xa8}\xacu\x89r\xfbn\x83\x0fu\xe1\xebZ&\x18\xd6}\x84\xc4\x1d\x92\xf1@VV\xdc\x0e?'
        # 定义 '/' 路由
        # 使用 session，判断用户是否已经登录
        @app.route('/')
        def index():
            if 'username' in session:
                return "Logged in as %s. <a href='/logout'>Logout</a>" % session['username']
            return "You're not logged in. <a href='/login'>Login</a>"
        # 登录系统
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            return '''
                <form method='POST' action='/login'>
                    <p>
                        <input type='text' name='username'/>
                    </p>
                    <p>
                        <input type='submit' value='Login'>
                    </p>
                </form>
            '''
        # 退出系统
        @app.route('/logout')
        def logout():
            session.pop('username', None)
            return redirect(url_for('index'))
    ```
## 重定向和错误
- 使用 `redirect()` 方法可以实现重定向，上面 `session` 部分的登录和退出系统功能都使用了重定向
- 使用 `abort(errno)` 方法可以退出请求，并返回一个错误代码
- 使用 `errorhandler()` 装饰器可以定制错误页面
- 示例：
    ```
        # 错误处理函数
        @app.errorhandler(404)
        def notfound(err):
            return render_template('404.html'), 404
    ```