__author__ = 'Cameron'
APPLICATION_NAME = "Stock Loan App"

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

# Create a Flask instance
app = Flask(__name__)
app.secret_key = 'development key'
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

import stock_loan_app.routes
