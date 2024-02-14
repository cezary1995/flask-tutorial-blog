import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from flaskr.forms import RegistrationForm, LoginForm
from flaskr.user import RegisterUser, LoginUser, UpdateUser
from instance.db_connector import Connector
from flaskr.forms import UpdateProfileForm
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = RegisterUser(form.name.data, form.username.data, form.email.data, form.password.data, form.confirm.data)
        db = Connector()
        result = db.create_user(user.name, user.username, user.email, user.password)
        if result == "Successfully registered":
            flash(result, 'success')
            return redirect(url_for("auth.login"))
        else:
            flash(result, 'danger')

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user = LoginUser(form.email.data, form.password.data)
        db = Connector()
        error = None
        user = db.sign_in_user(login_user.email)

        if login_user.email is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], login_user.password):
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
    db = Connector()
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.conn.execute(
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


@bp.route('/update_profile', methods=('GET', 'POST'))
def update_profile():
    form = UpdateProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        update = UpdateUser(form.name.data, form.username.data, form.email.data)

        db = Connector()
        result = db.update_user_info(update.name, update.username, update.email, g.user['id'])
        if result == "Your data has been updated successfully":
            flash(result, 'success')
            return redirect(url_for('blog.profile'))
        else:
            flash(result, 'error')

    return render_template('blog/update_profile.html')
