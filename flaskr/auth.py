import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

valid_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
valid_pswd = r'^.{3,}$'


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        # Check if all required fields are filled in
        if not name:
            error = 'name is required.'
        elif not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        # Check if email and password match the pattern
        if not check_if_match_pattern(valid_email, email):
            error = "Invalid email."
        elif not check_if_match_pattern(valid_pswd, password):
            error = "Invalid password."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, username, email, password) VALUES (?, ?, ?, ?)",
                    (name, username, email, generate_password_hash(password)),
                )
                # commit() needs to be called to save the changes.
                db.commit()
            # Check if used email and username are already in db
            except db.IntegrityError:
                if check_if_value_exist_in_db('username', username):
                    error = f"User {username} is already registered."
                elif check_if_value_exist_in_db('email', email):
                    error = f"Email {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# before_app_request - registers a function that runs before the view function, no matter what URL is requested
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# This decorator returns a new view function that wraps the original view it’s applied to. The new function checks
# if a user is loaded and redirects to the login page otherwise. If a user is loaded the original view is called and
# continues normally. You’ll use this decorator when writing the blog views.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def check_if_match_pattern(regex, obj):
    return True if re.fullmatch(regex, obj) else False


def check_if_value_exist_in_db(key, value):
    db = get_db()
    query = f"SELECT * FROM user WHERE {key}='{value}'"
    result = db.execute(query).fetchone()

    return True if result is not None else False


