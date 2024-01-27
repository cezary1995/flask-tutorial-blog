
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
