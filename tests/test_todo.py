import pytest
from todo.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert response.status_code == 302
    assert 'auth/login' in response.headers['Location']
    # assert b'Login' in response.data
    # assert b'Register' in response.data

    auth.login()
    response = client.get('/')
    assert b'Logout' in response.data
    assert b'Test task 1' in response.data
    assert b'A' in response.data
    assert b'5min' in response.data
    assert b"href='update/1'" in response.data
    assert b"href='done/1'" in response.data
    assert b"href='delete/1'" in response.data


@pytest.mark.parametrize('path', (
    '/update/1',
))
def test_login_required_post(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


@pytest.mark.parametrize('path', (
    '/done/1',
    '/delete/1',
))
def test_login_required_get(client, path):
    response = client.get(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


@pytest.mark.parametrize('path', (
    '/update/1',
))
def test_user_required_post(app, client, auth, path):
    # change todo user to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE todos SET user_id = 2 WHERE id = 1')
        db.commit()

    auth.login()

    # current user can't modify another user's todo items
    assert client.post(path).status_code == 403

    # current user doesn't see the update link
    assert b'href="/update/1"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/done/1',
    '/delete/1',
))
def test_user_required_get(app, client, auth, path):
    # change todo user to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE todos SET user_id = 2 WHERE id = 1')
        db.commit()

    auth.login()

    # current user can't modify another user's todo items
    assert client.get(path).status_code == 403

    # # current user doesn't see the update link
    # assert b'href="/update/1"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/update/4',
))
def test_exists_required_post(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


@pytest.mark.parametrize('path', (
    '/done/4',
    '/delete/4',
))
def test_exists_required_get(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/').status_code == 200
    client.post('/', data={'descr': 'created', 'time': '1min', 'priority': 'A'})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM todos').fetchone()[0]
        assert count == 4


def test_update(client, auth, app):
    auth.login()
    assert client.get('/update/1').status_code == 200
    client.post(
        'update/1',
        data={'descr': 'updated', 'time': '5h', 'priority': 'C'}
        )

    with app.app_context():
        db = get_db()
        todo = db.execute('SELECT * FROM todos WHERE id = 1').fetchone()
        assert todo['descr'] == 'updated'
        assert todo['time'] == '5h'
        assert todo['priority'] == 'C'


def test_done(client, auth, app):
    auth.login()

    with app.app_context():
        db = get_db()
        todo = db.execute('SELECT * FROM todos WHERE id = 1').fetchone()
        assert bool(todo['done']) is False

    client.get('/done/1')

    with app.app_context():
        db = get_db()
        todo = db.execute('SELECT * FROM todos WHERE id = 1').fetchone()
        assert bool(todo['done']) is True


@pytest.mark.parametrize('path', (
    # '/',
    '/update/1',
))
def test_create_update_validate(client, auth, path):
    auth.login()

    response = client.post(path, data={'descr': '', 'priority': 'A', 'time': '5min'})
    assert b'Description is required.' in response.data

    response = client.post(path, data={'descr': 'Test task 1', 'priority': 'A', 'time': ''})
    assert b'Time estimate is required.' in response.data

    response = client.post(path, data={'descr': 'Test task 1', 'priority': '', 'time': '5min'})
    assert b'Priority is required.' in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.get('/delete/1')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        todo = db.execute('SELECT * FROM todos WHERE id = 1').fetchone()
        assert todo is None
