import sqlite3
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash
from sys import argv
import re


class Connector:
    def __init__(self) -> None:
        self.db_name = current_app.config['DATABASE']
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        # Using this enables to use user['id'] instead of user[0]
        self.user = self.get_object_g()

    def get_object_g(self):
        g.db = self.conn
        g.db.row_factory = sqlite3.Row
        return g.db

    @click.command('init-db')
    def init_db(self) -> None:
        with current_app.open_resource(r"instance\schema.sql", 'r') as sql_setup:
            if len(argv) > 1 and current_app.config['INIT_DB'] == argv[3]:
                self.conn.executescript(sql_setup.read())
                print("Initializing db succeed")
            else:
                print("nie działa")

    def init_db_command(self) -> None:
        self.init_db()
        click.echo('Initialized the database.')

    def close_db(self, e=None):
        db = g.pop('db', None)

        if db is not None:
            db.close()

    def init_app(self, app):
        # tells Flask to call that function when cleaning up after returning the response.
        app.teardown_appcontext(self.close_db)
        # adds a new command that can be called with the flask command.
        app.cli.add_command(self.init_db)

    def create_user(self, name: str, username: str, email: str, password: str):
        success_msg = "Successfully registered"
        # Checking if email and password match pattern
        error = None
        if not self.check_if_match_pattern(self.get_email_pattern(), email):
            error = "Invalid email."
        if not self.check_if_match_pattern(self.get_password_pattern(), password):
            error = "Invalid password."
        if error is None:
            # Create new record in db
            try:
                self.conn.execute("INSERT INTO user (name, username, email, password) VALUES (?, ?, ?, ?)",
                                  (name, username, email, generate_password_hash(password)))
                self.conn.commit()
            except self.conn.IntegrityError as e:
                if self.check_if_value_exist_in_db('username', username):
                    error = f"{e}: User {username} is already registered."
                elif self.check_if_value_exist_in_db('email', email):
                    error = f"{e}:Email {email} is already registered."
            return error if error is not None else success_msg

    def update_user_info(self, name: str, username: str, email: str, id):
        success_msg = "Your data has been updated successfully"
        error = None
        if not self.check_if_match_pattern(self.get_email_pattern(), email):
            error = "Invalid email."
        if error is None:
            try:
                self.conn.execute('UPDATE user SET name = ?, username = ?, email = ?'
                                  ' WHERE id = ?', (name, username, email, id))
                self.conn.commit()
            except self.conn.IntegrityError as e:
                if self.check_if_value_exist_in_db('username', username):
                    error = f"User {username} is already registered."
                elif self.check_if_value_exist_in_db('email', email):
                    error = f"Email {email} is already registered."
        return error if error is not None else success_msg

    @staticmethod
    def get_email_pattern():
        return r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    @staticmethod
    def get_password_pattern():
        return r'^.{3,}$'

    def sign_in_user(self, email: str, ):
        return self.conn.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

    def get_posts(self):
        result = self.conn.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()
        return result

    def create_post(self, title, body, author_id):
        self.conn.execute('INSERT INTO post (title, body, author_id)'
                          ' VALUES (?, ?, ?)', (title, body, author_id))
        self.conn.commit()

    def update_post(self, title, body, id):
        self.conn.execute('UPDATE post SET title = ?, body = ?'
                          ' WHERE id = ?', (title, body, id))
        self.conn.commit()

    def delete(self, post_id):
        self.conn.execute('DELETE FROM post WHERE id = ?', (post_id,))
        self.conn.commit()

    @staticmethod
    def check_if_match_pattern(regex, obj):
        return True if re.fullmatch(regex, obj) else False

    def check_if_value_exist_in_db(self, db_value: str, form_value: str) -> bool:
        """
        Return true if db query returns a record, otherwise return False
        :param db_value: repr. database table's column name
        :param form_value: repr. the user form entry
        :return: True or False
        """
        with sqlite3.connect(self.db_name) as con:
            result = con.execute(f"SELECT * FROM user WHERE {db_value}='{form_value}'").fetchone()

            return True if result is not None else False

    def get_max_id_user(self):
        max_id = self.conn.execute('SELECT MAX(id) FROM user').fetchone()[0]
        return max_id

