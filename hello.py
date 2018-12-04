from flask import Flask, request, render_template
from flask import session, redirect, url_for

# 创建 Flask 类实例
app = Flask(__name__)
# 配置密钥
app.config['SECRET_KEY'] = b'\x82\xe0\x94\xa8}\xacu\x89r\xfbn\x83\x0fu\xe1\xebZ&\x18\xd6}\x84\xc4\x1d\x92\xf1@VV\xdc\x0e?'

# 定义路由，当浏览器请求定义的路由时触发响应的函数
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

# 错误处理函数
@app.errorhandler(404)
def notfound(err):
    return render_template('404.html'), 404