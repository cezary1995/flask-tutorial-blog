from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort
from flask import current_app
from flaskr.auth import login_required
from flaskr.forms import CreateForm, UpdateForm
from instance.db_connector import Connector
from flaskr.user import CreatePost, UpdatePost

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = Connector()
    posts = db.get_posts()

    return render_template('blog/index.html', posts=posts)


@bp.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(current_app.config['UPLOADED_PHOTOS_DEST'], filename)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = CreateForm(request.form)
    if request.method == 'POST' and form.validate():
        post = CreatePost(form.title.data, form.body.data)
        img = request.files['photo']
        path = r'flaskr\uploads\''
        img.save(path + img.filename)
        error = None

        if not post.title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = Connector()
            db.create_post(post.title, post.body, g.user['id'])
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    form = UpdateForm(request.form)
    if request.method == 'POST' and form.validate():
        post_update = UpdatePost(form.title.data, form.body.data)
        error = None
        if not post_update.title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = Connector()
            db.update(post_update.title, post_update.body, id)
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = Connector()
    db.delete(id)
    return redirect(url_for('blog.index'))


@bp.route('/profile')
def profile():
    return render_template('blog/profile.html')


def get_post(id, check_author=True):
    db = Connector()
    post = db.conn.execute(
         'SELECT p.id, title, body, created, author_id, username'
         ' FROM post p JOIN user u ON p.author_id = u.id'
         ' WHERE p.id = ?',
         (id,)
     ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post
