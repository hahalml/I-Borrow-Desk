from werkzeug import generate_password_hash, check_password_hash

from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(250))
    receive_email = db.Column(db.Boolean, index=True)
    admin = db.Column(db.Boolean)
    _views = db.Column(db.Integer)

    def __init__(self, username, password, email, receive_email=True, admin=False):
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

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def is_admin(self):
        return self.admin

    def increment_views(self):
        self._views += 1

    def __repr__(self):
        return '{}'.format(self.username)


def authenticate(username, password):
    """Authentication handler for Flask-JWT"""
    print('User {} logged in'.format(username))
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user


def identity(payload):
    """Return the userinside the payload"""
    return User.query.get(payload['identity'])