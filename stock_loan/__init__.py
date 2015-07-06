
APPLICATION_NAME = "Stock Loan App"

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from flask_admin import Admin

# Create a Flask instance
app = Flask(__name__)
app.config.from_object('flask_config')
#sslify = SSLify(app, skips=['main_page', 'about', 'faq'])
admin = Admin(app)


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

import stock_loan.routes
from routes import *

admin.add_view(AdminView(name='Home'))
admin.add_view(DbView(User, db.session))



#Build the database
db.create_all()


# Program launcher - in debug mode
if __name__ == '__main__':
    app.run()


