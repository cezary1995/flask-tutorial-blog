import os
from flask import Flask


def create_app(test_config=None):
    # 1. __name__ - the name of the current Python module. The app needs to know where it’s located to set up some paths
    # 2. instance_relative: jest sposobem na konfigurację aplikacji, które pozwala na łatwe zarządzanie konfiguracją dla
    # różnych środowisk (rozwój, testowanie, produkcja) poprzez wykorzystanie instancji konfiguracyjnych. Flask
    # będzie szukać plików konfiguracyjnych w folderze "instance" znajdującym się w katalogu głównym
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

        # ensure the instance folder exists, it is needed because there will be created database file
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # route create a connection between th eURL  and function that returns a response
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    # This function takes an application and does the registration.
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
