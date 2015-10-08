__author__ = 'Cameron'
from . import db
from werkzeug import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(250))
    receive_email = db.Column(db.Boolean, index=True)
    admin = db.Column(db.Boolean)
    _views = db.Column(db.Integer)

    def __init__(self, username, password, email, receive_email=True, admin = False):
        self.username = username
        self.set_password(password)
        self.email = email
        self.receive_email = receive_email
        self.admin = admin
        self._views = 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def is_admin(self):
        return self.admin

    def increment_views(self):
        self._views += 1

