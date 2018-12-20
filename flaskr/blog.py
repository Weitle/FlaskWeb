# 定义博客蓝图并注册到应用工厂
from flask import Blueprint, render_template, request, flash, g, redirect, url_for
from werkzeug.exceptions import abort

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
            db.execute("insert into post(title, body, author_id) values (?, ?, ?)", (title, body, g.user['id']))
            db.commit()
        return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    # 根据给定的 id 获取相应的 post
    post = get_post(id)
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
            db.execute('update post set title = ?, body = ? where id = ?', (title, body, id))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('delete from post where id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

def get_post(id, check_author=True):
    db = get_db()
    post = db.execute("select p.id, title, body, created, author_id, username from post p join user u on p.author_id = u.id where p.id = ?", (id,)).fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post
