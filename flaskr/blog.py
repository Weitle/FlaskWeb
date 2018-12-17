# 定义博客蓝图并注册到应用工厂
from flask import Blueprint, render_template, request, flash, g, redirect, url_for

from .db import get_db
from .auth import login_required

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'select p.id, title, body, created, author_id, username'
        ' from post p join user u on p.author_id = u.id'
        ' order by created desc'
    ).fetchall()
    return render_template('blog/index.html', posts = posts)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        error = None
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("instert into post(title, body, author_id) values (?, ?, ?, ?)", (title, body, g.user['id']))
            db.commit()
        return redirect(url_for('blog.index'))
    return render_template('blog/create.html')