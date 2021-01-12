from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)


@bp.route('/', methods=['GET'])
def index():
    db = get_db()
    todos = db.execute(
        'SELECT t.id, descr, priority, time, done, user_id'
        ' FROM todos t JOIN user u on t.user_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('todo/index.html', todo_list=todos)


@bp.route('/', methods=['POST'])
def add_item():
    descr = request.form.get('descr')
    time = request.form.get('time')
    priority = request.form.get('priority')
    error = None

    if not request.form.get('descr') and isinstance(request.form.get('descr'), str):
        error = 'Description is required.'
    if not request.form.get('time') and isinstance(requst.form.get('time'), str):
        error = 'Time estimate is required.'
    if not request.form.get('priority') and request.form.get('priority') in ['A', 'B', 'C']:
        error = 'Priority is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO todos (user_id, descr, priority, time)'
            ' VALUES (?, ?, ?, ?)',
            (g.user['id'], request.form.get('descr'), request.form.get('priority'),
             request.form.get('time'))
        )
        db.commit()

    return redirect(url_for('todo.index'))
