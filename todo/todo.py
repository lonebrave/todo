from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    db = get_db()
    todos = db.execute(
        'SELECT t.id, descr, priority, time, done, user_id'
        ' FROM todos t JOIN user u on t.user_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC', (g.user['id'],)
    ).fetchall()
    return render_template('todo/index.html', todo_list=todos)


@bp.route('/', methods=['POST'])
@login_required
def add_item():
    descr = request.form.get('descr')
    time = request.form.get('time')
    priority = request.form.get('priority')
    error = None

    if not request.form.get('descr') or not isinstance(request.form.get('descr'), str):
        error = 'Description is required.'
    if not request.form.get('time') or not isinstance(request.form.get('time'), str):
        error = 'Time estimate is required.'
    if not request.form.get('priority') or request.form.get('priority') not in ['A', 'B', 'C']:
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


def get_todo(todo_id, check_user=True):
    db = get_db()
    todo = db.execute(
        'SELECT t.id, descr, priority, time, done, user_id'
        ' FROM todos t JOIN user u on t.user_id = u.id'
        ' WHERE t.id = ?', (todo_id,)
    ).fetchone()

    if todo is None:
        abort(404, "Todo id {todo_id} doesn't exist.")

    if check_user and todo['user_id'] != g.user['id']:
        abort(403)

    return todo


@bp.route('/update/<int:todo_id>', methods=['GET'])
@login_required
def update(todo_id):
    todo = get_todo(todo_id)

    return render_template('todo/update.html', todo=todo)


@bp.route('/update/<int:todo_id>', methods=['POST'])
@login_required
def update_todo(todo_id):
    todo = get_todo(todo_id)
    descr = request.form.get('descr')
    time = request.form.get('time')
    priority = request.form.get('priority')
    error = None

    if not request.form.get('descr') or not isinstance(request.form.get('descr'), str):
        error = 'Description is required.'
    if not request.form.get('time') or not isinstance(request.form.get('time'), str):
        error = 'Time estimate is required.'
    if not request.form.get('priority') or request.form.get('priority') not in ['A', 'B', 'C']:
        error = 'Priority is required.'

    if error is not None:
        flash(error)
        return render_template('todo/update.html', todo=todo)
    else:
        db = get_db()
        db.execute(
            'UPDATE todos SET descr = ?, priority = ?, time = ?'
            ' WHERE id = ?',
            (descr, priority, time, todo_id)
        )
        db.commit()

    return redirect(url_for('todo.index'))


@bp.route('/delete/<int:todo_id>', methods=['GET'])
@login_required
def delete(todo_id):
    # call get_todo to verify todo exists and user is correct
    get_todo(todo_id)

    db = get_db()
    db.execute(
        'DELETE FROM todos WHERE id = ?',
        (todo_id,)
    )
    db.commit()

    return redirect(url_for('todo.index'))


@bp.route('/done/<int:todo_id>', methods=['GET'])
@login_required
def done(todo_id):
    # call get_todo to verify todo exists and user is correct
    get_todo(todo_id)

    db = get_db()
    db.execute(
        'UPDATE todos SET done = TRUE WHERE id = ?',
        (todo_id,)
    )
    db.commit()

    return redirect(url_for('todo.index'))
