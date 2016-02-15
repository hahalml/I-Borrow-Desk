import os
import logging
from datetime import datetime
import time

from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import NotFound
from apscheduler.schedulers.background import BackgroundScheduler

from . import app, login_manager, db, stock_loan, mc, limiter
from .models import User
from .email_update import send_emails
from .utils import historical_report_cache, view_logger

dirname, filename = os.path.split(os.path.abspath(__file__))

# TEMPLATES
REGISTER_TEMPLATE = 'register_template.html'
CHANGE_PASSWORD_TEMPLATE = 'change_password_template.html'
CHANGE_EMAIL_TEMPLATE = 'change_email_template.html'
LOGIN_TEMPLATE = 'login_template.html'
MAIN_PAGE_TEMPLATE = 'mainpage_template.html'
WATCH_LIST_TEMPLATE = 'watch_list_template.html'
HISTORICAL_REPORT_TEMPLATE = 'historical_report_template.html'
NAME_SEARCH_TEMPLATE = 'name_search_template.html'
FILTER_TEMPLATE = 'filter_template.html'
ABOUT_TEMPLATE = 'about_template.html'
FAQ_TEMPLATE = 'faq_template.html'
TRENDING_TEMPLATE = 'trending_template.html'

logging.basicConfig()

login_manager.login_view = 'login'

ADMIN_HOMEPAGE_TEMPLATE = 'admin_homepage_template.html'


class AdminView(BaseView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin
        else:
            return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            raise NotFound

    @expose('/')
    def index(self):
        if not self.is_accessible():
            raise NotFound
        else:
            return self.render(ADMIN_HOMEPAGE_TEMPLATE)


class DbView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin
        else:
            return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            raise NotFound


@login_manager.user_loader
def load_user(userid):
    """Required function for Flask-Login"""
    return User.query.get(int(userid))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


@app.route('/admin_login', methods=['GET', 'POST'])
@limiter.limit("30 per hour")
@limiter.limit("10 per minute")
def admin_login():
    """Login page handler"""
    if request.method == 'GET':
        return render_template(LOGIN_TEMPLATE)

    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        raise NotFound
    if not user.is_admin:
        raise NotFound

    # Flask login
    login_user(user)

    flash('Welcome {}!'.format(user.username))
    print('User: {} logged in'.format(user.username))
    return 'logged in', 200

@app.route('/admin_logout')
@login_required
def admin_logout():
    logout_user()
    return 'logged out', 200


@app.before_first_request
def initialize():
    """Initialize the scheduler for recurring jobs"""
    apsched = BackgroundScheduler()
    apsched.start()

    # Add a job - morning emails
    apsched.add_job(email_job, 'cron',
                    day_of_week='mon-fri', hour='9', minute='4',
                    timezone='America/New_York')

    # Refresh trending stocks and collective stats on the hour
    apsched.add_job(refresh_borrow, 'cron', minute='5')


def email_job():
    """Helper function for scheduled email sender function"""
    users = User.query.filter_by(receive_email=True).all()
    send_emails(users, stock_loan)


def refresh_borrow():
    """Helper function for refreshing instance summary data for the Borrow object
    Does NOT perform any actual database updates"""
    stock_loan.update_trending()
    stock_loan.refresh_all_symbols()
    stock_loan.refresh_latest_all_symbols()
    print("Refreshed Local Borrow data")

