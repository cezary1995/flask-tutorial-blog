import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.forms import RegistrationForm, LoginForm
from flaskr.user import RegisterUser, LoginUser
from instance.db_connector import Connector
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = RegisterUser(form.name.data, form.username.data, form.email.data, form.password.data, form.confirm.data)
        db = Connector()
        result = db.create_user(user.name, user.username, user.email, user.password)
        if result == "Successfully registered":
            return redirect(url_for("auth.login"))
        else:
            error = result
        flash(error)
    return render_template('auth/register_2.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user = LoginUser(form.email.data, form.password.data)
        db = Connector()
        error = None
        user = db.sign_in_user(login_user.email)
        print(user)
        user_id = user['id']
        user_pswd_hash = user['password']
        if login_user.email is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user_pswd_hash, login_user.password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user_id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# before_app_request - registers a function that runs before the view function, no matter what URL is requested
# @bp.before_app_request
# def load_logged_in_user():
#     db = Connector()
#     user_id = session.get('user_id')
#
#     if user_id is None:
#         g.user = None
#     else:
#         g.user = db.execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()


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




