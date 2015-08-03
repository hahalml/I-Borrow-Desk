from __future__ import absolute_import
import threading

APPLICATION_NAME = "Stock Loan App"

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

from .routes import *


admin.add_view(AdminView(name='Home'))
admin.add_view(DbView(User, db.session))


from . import twitter

#Start separate thread to run the twitter bot after confirming not running locally
twitter_thread = threading.Thread(target=twitter.run_twitter_stream)
twitter_thread.start()


#Build the database
db.create_all()



