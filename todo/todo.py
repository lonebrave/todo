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


@bp.route('/update/<int:todo_id>', methods=['GET'])
def update(todo_id):
    db = get_db()
    todo = db.execute(
        'SELECT t.id, descr, priority, time, done, user_id'
        ' FROM todos t JOIN user u on t.user_id = u.id'
        ' WHERE t.id = ?', (todo_id,)
    ).fetchone()

    if todo is None:
        abort(404, "Todo id {todo_id} doesn't exist.")

    return render_template('todo/update.html', todo=todo)


@bp.route('/update/<int:todo_id>', methods=['POST'])
def update_post(todo_id):
    descr = request.form.get('descr')
    time = request.form.get('time')
    priority = request.form.get('priority')
    error = None

    if not request.form.get('descr') and isinstance(request.form.get('descr'), str):
        error = 'Description is required.'
    if not request.form.get('time') and isinstance(request.form.get('time'), str):
        error = 'Time estimate is required.'
    if not request.form.get('priority') and request.form.get('priority') in ['A', 'B', 'C']:
        error = 'Priority is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        todo = db.execute(
            'SELECT t.id, descr, priority, time, done, user_id'
            ' FROM todos t JOIN user u on t.user_id = u.id'
            ' WHERE t.id = ?', (todo_id,)
        ).fetchone()

        if todo is None:
            abort(404, "Todo id {todo_id} doesn't exist.")
        else:
            db.execute(
                'UPDATE todos SET descr = ?, priority = ?, time = ?'
                ' WHERE id = ?',
                (descr, priority, time, todo_id)
            )
            db.commit()

    return redirect(url_for('todo.index'))


@bp.route('/delete/<int:todo_id>', methods=['GET'])
def delete(todo_id):
    db = get_db()
    db.execute(
        'DELETE FROM todos WHERE id = ?',
        (todo_id,)
    )
    db.commit()

    return redirect(url_for('todo.index'))


@bp.route('/done/<int:todo_id>', methods=['GET'])
def done(todo_id):
    db = get_db()
    todo = db.execute(
        'SELECT t.id, descr, priority, time, done, user_id'
        ' FROM todos t JOIN user u on t.user_id = u.id'
        ' WHERE t.id = ?', (todo_id,)
    ).fetchone()

    if todo is None:
        abort(404, "Todo id {todo_id} doesn't exist.")
    else:
        db.execute(
            'UPDATE todos SET done = TRUE WHERE id = ?',
            (todo_id,)
        )
        db.commit()

    return redirect(url_for('todo.index'))
