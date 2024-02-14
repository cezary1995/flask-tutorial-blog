from wtforms import Form, FileField, StringField, PasswordField, validators


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=3, max=25), validators.DataRequired()])
    username = StringField('Username', [validators.Length(min=3, max=25), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=5, max=35), validators.DataRequired()])
    password = PasswordField('New Password', [
        validators.Length(min=2, max=25), validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password', [validators.DataRequired()])
    # accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class LoginForm(Form):
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField([validators.DataRequired()])


class CreatePostForm(Form):

    title = StringField('Title', [validators.DataRequired()])
    body = StringField('Body', [validators.DataRequired()])
    img = FileField('img')


class UpdatePostForm(Form):
    title = StringField('Title', [validators.DataRequired()])
    body = StringField('Body', [validators.DataRequired()])
    img = FileField('img')


class UpdateProfileForm(Form):
    name = StringField('Name', [validators.Length(min=3, max=25)])
    username = StringField('Username', [validators.Length(min=3, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=25)])
