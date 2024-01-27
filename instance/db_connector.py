import sqlite3, os, json
import hashlib, binascii, os
import click
from flask import current_app, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
from sys import argv
import re


class Connector:
    def __init__(self) -> None:
        self.db_name = current_app.config['DATABASE']
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.get_g()

    def __del__(self):
        self.conn.close()

    def get_g(self):
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
        g.db.rowfactory = 'p'

        if db is not None:
            db.close()

    def init_app(self, app):
        # tells Flask to call that function when cleaning up after returning the response.
        app.teardown_appcontext(self.close_db)
        # adds a new command that can be called with the flask command.
        app.cli.add_command(self.init_db)

    def create_user(self, name: str, username: str, email: str, password: str,
                 re_email=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', re_pswd=r'^.{3,}$'):
        error = None
        if not self.check_if_match_pattern(re_email, email):
            error = "Invalid email."
        elif not self.check_if_match_pattern(re_pswd, password):
            error = "Invalid password."
        if error is None:
            try:
                self.conn.execute("INSERT INTO user (name, username, email, password) VALUES (?, ?, ?, ?)",
                                  (name, username, email, generate_password_hash(password)))
                self.conn.commit()
            except self.conn.IntegrityError as e:
                if self.check_if_value_exist_in_db('username', username):
                    error = f"{e}: User {username} is already registered."

                elif self.check_if_value_exist_in_db('email', email):
                    error = f"{e}:Email {email} is already registered."
            return error if error is not None else "Successfully registered"

    def sign_in_user(self, email: str,):
        return self.conn.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()



    def check_if_match_pattern(self, regex, obj):
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
