# Flask Web Development
- Flask Web 开发学习笔记
- 使用 Python 3.7 和 Flask 1.0.2
- 使用 Anaconda 生成名为 flask1.0 的虚拟环境
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
- 创建一个 hello.py 文件
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
    - 运行应用前首先定义环境变量 FLASK_APP
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
        - 此时应用默认运行在 127.0.0.1(localhost) 的 5000 端口，这时只有自己的机器可以访问服务，而网络中的其他客户端无法访问服务
        - 可以通过设置 --host 参数为 0.0.0.0 让服务器可以被公开访问，设置 --port 参数设置服务运行的端口
            ```
                flask run --host 0.0.0.0 --port 8080
            ```
        - 调试模式：
            - 可以在服务器运行之前设置环境变量 FLASK_ENV=development
            - 也可以在应用中配置 FLASK_DEBUG=1
            - 不要在生产环境中启动调试模式

## 路由
- 使用 route() 装饰器把函数绑定到路由上
- 可以设置动态路由
### 路由变量规则
- 通过 URL 的一部分标记为 `<variable_name>`</code>` 就可以在 URL 中添加变量，标记的部分会作为关键字参数传递给函数
    ```
        @app.route('/user/<username>')
        def user(username):
            return "<h1>User %s</h1>" % username
    ```
- 还可以通过 `<converter:variable_name>` 为标记设置转换类型，可设置的类型有：string, int, float, path, uuid
    ```
        @app.route('/post/<int:postid>')
        def post(postid):
            return "<h1>Post #%d</h1>" % postid
    ```
