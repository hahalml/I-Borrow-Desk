import os
import logging
import random
import thread
import string

from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from apscheduler.schedulers.background import BackgroundScheduler

from stock_loan import app, login_manager, db
from models import User
from borrow import Borrow
from email_update import send_emails
from forms import RegistrationForm, ChangePasswordForm, ChangeEmailForm, FilterForm
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

dirname, filename = os.path.split(os.path.abspath(__file__))

# TEMPLATES
REGISTER_TEMPLATE = 'register_template.html'
CHANGE_PASSWORD_TEMPLATE = 'change_password_template.html'
CHANGE_EMAIL_TEMPLATE = 'change_email_template.html'
LOGIN_TEMPLATE = 'login_template.html'
MAIN_PAGE_TEMPLATE = 'mainpage_template.html'
WATCH_LIST_TEMPLATE = 'watch_list_template.html'
HISTORICAL_REPORT_TEMPLATE = 'historical_report_template.html'
FILTER_TEMPLATE = 'filter_template.html'
ABOUT_TEMPLATE = 'about_template.html'
FAQ_TEMPLATE = 'faq_template.html'

logging.basicConfig()

login_manager.login_view = 'login'

ADMIN_HOMEPAGE_TEMPLATE = 'admin_homepage_template.html'


class AdminView(BaseView):
    def is_accessible(self):
        if current_user.is_authenticated():
            return current_user.is_admin()
        else:
            return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login'))

    @expose('/')
    def index(self):
        return self.render(ADMIN_HOMEPAGE_TEMPLATE)


class DbView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated():
            return current_user.is_admin()
        else:
            return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login'))


@login_manager.user_loader
def load_user(userid):
    """Required function for Flask-Login"""
    return User.query.get(int(userid))


@app.route('/')
def main_page():
    """Mainpage handler"""
    symbols = [random.choice(stock_loan.latest_symbols) for i in xrange(0, 15)]
    summary = stock_loan.summary_report(symbols)
    number_of_symbols = stock_loan.all_symbols_count
    return render_template(MAIN_PAGE_TEMPLATE, summary=summary, number_of_symbols=number_of_symbols)


@app.route('/watchlist', methods=['GET', 'POST'])
@login_required
def watch_list():
    """Watchlist handler"""

    # If the user added or removed symbols from their watchlist make the changes then re-render the watchlist
    if request.method == 'POST':
        symbols = request.form['symbols'].replace(' ', '').split(',')
        symbols_to_remove = request.form['remove-symbols'].replace(' ', '').split(',')
        if symbols != ['']:

            # Insertion/deletion method returns two lists - symbols added, and symbols that failed to be added
            # Render some user feedback with flashed messages
            symbols_added, symbols_failed_to_be_added = stock_loan.insert_watchlist(current_user.id, symbols)
            if symbols_added:
                for symbol in symbols_added:
                    flash("Added %s to your watchlist" % symbol)
            if symbols_failed_to_be_added:
                for symbol in symbols_failed_to_be_added:
                    flash("Failed to add %s to your watchlist" % symbol)

        if symbols_to_remove != ['']:
            symbols_removed = stock_loan.remove_watchlist(current_user.id, symbols_to_remove)
            if symbols_removed:
                for symbol in symbols_removed:
                    flash("Removed %s from your watchlist" % symbol)

    # Get user's watchlist summary
    watchlist = stock_loan.get_watchlist(current_user.id)
    summary = stock_loan.summary_report(watchlist)

    return render_template(WATCH_LIST_TEMPLATE, summary=summary)


@app.route('/historical_report', methods=['GET'])
def historical_report():
    """Historical report handler, uses url arguments to determine the symbol to report
    on and the time period (last few days every 15mins or daily long-term)"""

    # Grab the symbol and real-time flag form the url
    symbol = request.args['symbol'].upper()
    if request.args['real_time'] == 'True':
        real_time = True
    else:
        real_time = False

    summary = []
    name = ''

    # Generate a report based on the url parameters
    if symbol:
        name, summary = stock_loan.historical_report(symbol, real_time)

    return render_template(HISTORICAL_REPORT_TEMPLATE, symbol=symbol, name=name, summary=summary)


@app.route('/filter', methods=['GET', 'POST'])
def filter():
    """Handler for the filter page"""
    form = FilterForm(request.form)
    if request.method == 'POST' and form.validate():
        summary = stock_loan.filter(min_available=form.min_available.data,
                                    max_available=form.max_available.data,
                                    min_fee=form.min_fee.data,
                                    max_fee=form.max_fee.data,
                                    order_by=form.order_by.data
                                    )
        if len(summary) == 100:
            flash('Results capped at 100')
        else:
            flash('Found %s results' %len(summary))
        return render_template(FILTER_TEMPLATE, form=form, summary=summary)
    else:
        return render_template(FILTER_TEMPLATE, form=form, summary = [])


@login_required
@app.route('/change_morning_email')
def change_morning_email():
    """Change morning email preference"""
    new_preference = request.args['receive']
    if new_preference == 'True':
        current_user.receive_email = True
        db.session.add(current_user)
        db.session.commit()
        flash('Now receiving morning emails')
    elif new_preference == 'False':
        current_user.receive_email = False
        db.session.add(current_user)
        db.session.commit()
        flash('No longer receiving morning emails')
    return redirect(url_for('watch_list'))


@login_required
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Change password handler"""
    form = ChangePasswordForm(request.form)

    if request.method == 'POST' and form.validate():
        if current_user.check_password(form.password.data):
            current_user.set_password(form.new_password.data)
            db.session.add(current_user)
            db.session.commit()
            flash('Password updated')
            return redirect(url_for('watch_list'))
        else:
            flash('Incorrect password entered')
            return redirect(url_for('change_password'))
    return render_template(CHANGE_PASSWORD_TEMPLATE, form=form)


@login_required
@app.route('/change_email', methods=['GET', 'POST'])
def change_email():
    """Change email handler"""
    form = ChangeEmailForm(request.form)
    if request.method == 'POST' and form.validate():
        if current_user.check_password(form.password.data):
            current_user.email = form.new_email.data
            db.session.add(current_user)
            db.session.commit()
            flash('Email changed to %s' % form.new_email.data)
            return redirect(url_for('watch_list'))
        else:
            flash('Incorrect password entered')
            return redirect(url_for('change_email'))
    return render_template(CHANGE_EMAIL_TEMPLATE, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page handler"""

    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        if User.query.filter_by(username=form.username.data).first() is not None:
            flash('Choose a different username')
            return redirect(url_for('register'))

        elif User.query.filter_by(email=form.email.data).first() is not None:
            flash('Someone with that email has already registered')
            return redirect(url_for('register'))

        else:
            user = User(form.username.data, form.password.data, form.email.data, form.receive_emails.data)
            db.session.add(user)
            db.session.commit()
            flash('User successfully registered')
            return redirect(url_for('login'))

    else:
        return render_template(REGISTER_TEMPLATE, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page handler"""
    if request.method == 'GET':
        return render_template(LOGIN_TEMPLATE)

    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash('Invalid username')
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash('Invalid password')
        return redirect(url_for('login'))

    # Flask login
    login_user(user)

    flash('Welcome %s!' % user.username)
    return redirect(url_for('watch_list'))


@app.route('/logout')
def logout():
    """Logs the user out"""
    logout_user()
    flash('Successfully logged out')
    return redirect(url_for('main_page'))


@app.route('/about')
def about():
    """Handler for about page"""
    return render_template(ABOUT_TEMPLATE)


@app.route('/faq')
def faq():
    """Handler for faq page"""
    return render_template(FAQ_TEMPLATE)


@app.before_first_request
def initialize():
    """Initialize the scheduler for recurring jobs"""
    apsched = BackgroundScheduler()
    apsched.start()

    # Add a job - morning emails
    apsched.add_job(email_job, 'cron', day_of_week='mon-fri', hour=9, minute=5, timezone='America/New_York')
    apsched.add_job(update_database, 'cron', day_of_week='mon-fri', minute='1-46/15', hour='8-17',
                    timezone='America/New_York')


def email_job():
    """Helper function for scheduled email sender function"""
    users = User.query.filter_by(receive_email=True).all()
    send_emails(users, stock_loan)


def update_database():
    """Helper function for updating database as scheduled"""
    stock_loan.update()

# Create a Borrow instance
stock_loan = Borrow(database_name='stock_loan', filename='usa', create_new=False)

import twitter

# Start separate thread to run the twitter bot after confirming not running locally
if string.find(dirname, 'vagrant') is None:
    thread.start_new_thread(twitter.run_twitter_stream, ())