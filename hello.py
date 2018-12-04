from flask import Flask, request, render_template

# 创建 Flask 类实例
app = Flask(__name__)

# 定义路由，当浏览器请求定义的路由时触发响应的函数
# 定义 '/' 路由
@app.route('/')
def index():
    return '<h1>Home Page</h1>'

# 定义 '/hello' 路由， 使用 render_template() 方法渲染模板
@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name = name)

# 定义动态路由
# 设置路由变量
@app.route('/user/<username>')
def user(username):
    return "<h1>User %s</h1>" % username

# 设置路由变量，并指定路由变量的类型
@app.route('/post/<int:postid>')
def post(postid):
    return "<h1>Post #%d</h1>" % postid

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
