# 数据库处理

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# 获取数据库连接
def get_db():
    if 'db' not in g:
        # 建立连接
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # 返回一行数据的操作
        g.db.row_factory = sqlite3.Row
    # 返回数据库连接
    return g.db

# 释放数据库连接
def close_db(err):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """
        Clear the exists data and create new tables.
    """
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

