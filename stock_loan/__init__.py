APPLICATION_NAME = "Stock Loan App"
import logging
from logging import StreamHandler
from logging.handlers import SMTPHandler, QueueHandler, QueueListener
import queue
import memcache
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from flask_admin import Admin
from flask_limiter import Limiter
from flask_jwt import JWT

from .borrow import Borrow

# Create a Flask instance
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
sslify = SSLify(app, skips=['main_page', 'about', 'faq'])
admin = Admin(app)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Set up JWT
from .models import authenticate, identity
jwt = JWT(app, authenticate, identity)

# Rate limiter app
limiter = Limiter(app)
limiter.logger.addHandler(StreamHandler())



stock_loan = Borrow(database_name='stock_loan2', create_new=False)

mc = memcache.Client(['127.0.0.1:11211'], debug=0)
mc.flush_all()

from .routes import *
from .ajax import *

admin.add_view(AdminView(name='Home'))
admin.add_view(DbView(User, db.session))

# Build the database
db.create_all()

# logging
if not app.debug:
    que = queue.Queue(-1)  # no limit on size
    # Create a QueueHandler to receive logging
    queue_handler = QueueHandler(que)
    queue_handler.setLevel(logging.ERROR)

    # Create the actual mail handler
    credentials = app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']
    mail_handler = SMTPHandler(('smtp.gmail.com', '587'),
                               app.config['APP_ADDRESS'],
                               [app.config['ADMIN_ADDRESS']],
                               'stock_loan exception',
                               credentials=credentials, secure=())

    # Create a listener handler to deque things from the QueueHandler and send to the mail handler
    listener = QueueListener(que, mail_handler)
    listener.start()

    # Add the queue handler to the app
    app.logger.addHandler(queue_handler)
