
class RegisterUser:
    def __init__(self, name, username, email, password, confirm):
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.confirm = confirm


class LoginUser:
    def __init__(self, email, password):
        self.email = email
        self.password = password


class CreatePost:
    def __init__(self, title, body):
        self.title = title
        self.body = body


class UpdatePost:
    def __init__(self, title, body):
        self.title = title
        self.body = body
