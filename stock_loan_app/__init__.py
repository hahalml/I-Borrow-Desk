
APPLICATION_NAME = "Stock Loan App"

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

# Create a Flask instance
app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

import stock_loan_app.routes

#Build the database
db.create_all()
