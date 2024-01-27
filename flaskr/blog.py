from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from flask_uploads import UploadSet, IMAGES, configure_uploads
from werkzeug.exceptions import abort
from flask import current_app
from flaskr.auth import login_required
# from flaskr.db import get_db
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import SubmitField
from instance.db_connector import Connector
bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    return "6"
    db = Connector()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
#     return render_template('blog/index.html', posts=posts)
#
#
# # UploadSet is collection of files
# photos = UploadSet('photos', IMAGES)
# configure_uploads(current_app, photos)


# It is used to validate the user's form
# class UploadForm(FlaskForm):
#     photo = FileField(
#         validators=[
#             FileAllowed(photos, 'Only images are allowed'),
#             FileRequired('File field should not be empty')
#         ]
#     )
#     submit = SubmitField('Upload')

@bp.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(current_app.config['UPLOADED_PHOTOS_DEST'], filename)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        img = request.files['photo']
        img.save(f'flaskr\\uploads\\{img.filename}')
        error = None

        if not title:
            error = 'Title is required.'

        # if error is not None:
        #     flash(error)
        # else:
        #     form = UploadForm()
        #     if form.validate_on_submit():
        #         filename = photos.save(form.photo.data)
        #         file_url = url_for('get_file', filename=filename)
        #     else:
        #         file_url = None
        #
        #     db = get_db()
        #     db.execute(
        #         'INSERT INTO post (title, body, author_id)'
        #         ' VALUES (?, ?, ?)',
        #         (title, body, g.user['id'])
        #     )
        #     db.commit()
        #     return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    pass
    # post = get_db().execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' WHERE p.id = ?',
    #     (id,)
    # ).fetchone()
    #
    # if post is None:
    #     abort(404, f"Post id {id} doesn't exist.")
    #
    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    # return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/profile')
def profile():
    return render_template('blog/profile.html')
