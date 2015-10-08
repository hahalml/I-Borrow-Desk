APPLICATION_NAME = "Stock Loan App"

import memcache

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from flask_admin import Admin

from .borrow import Borrow

# Create a Flask instance
app = Flask(__name__)
app.config.from_object('config')
sslify = SSLify(app, skips=['main_page', 'about', 'faq'])
admin = Admin(app)


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

stock_loan = Borrow(database_name='stock_loan', create_new=False)

mc = memcache.Client(['127.0.0.1:11211'], debug=0)
mc.flush_all()

from .routes import *
from .ajax import *

admin.add_view(AdminView(name='Home'))
admin.add_view(DbView(User, db.session))

#Build the database
db.create_all()
