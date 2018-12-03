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

# 定义动态路由
# 设置路由变量
@app.route('/user/<username>')
def user(username):
    return "<h1>User %s</h1>" % username
# 设置路由变量，并制定路由变量的类型
@app.route('/post/<int:postid>')
def post(postid):
    return "<h1>Post #%d</h1>" % postid