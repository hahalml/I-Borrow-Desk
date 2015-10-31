import os
import logging
from datetime import datetime
import time

from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from apscheduler.schedulers.background import BackgroundScheduler

from . import app, login_manager, db, stock_loan, mc, limiter
from .models import User
from .email_update import send_emails
from .forms import RegistrationForm, ChangePasswordForm, ChangeEmailForm, FilterForm
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
            return redirect(url_for('login'))

    @expose('/')
    def index(self):
        return self.render(ADMIN_HOMEPAGE_TEMPLATE)


class DbView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin
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
@view_logger
def main_page():
    """Mainpage handler"""

    number_of_symbols = stock_loan.all_symbols_count

    summary = mc.get('mainpage')
    if not summary:
        summary = stock_loan.filter_db(min_available=10000, min_fee=20, order_by='fee')
        summary = summary[:20]
        mc.set('mainpage', summary)
        print('mainpage cache miss')
    else:
        print('mainpage cache hit')

    return render_template(MAIN_PAGE_TEMPLATE, summary=summary,
                           number_of_symbols=number_of_symbols)


@app.route('/trending')
@view_logger
def trending():
    """Handler for the trending view"""

    trending_fee = mc.get('trending_fee')
    if not trending_fee:
        trending_fee = stock_loan.summary_report(stock_loan.trending_fee)
        mc.set('trending_fee', trending_fee)
        print('trending_fee cache miss')
    else:
        print('trending_fee cache hit')

    trending_available = mc.get('trending_available')
    if not trending_available:
        trending_available = stock_loan.summary_report(stock_loan.trending_available)
        mc.set('trending_available', trending_available)
        print('trending_available cache miss')
    else:
        print('trending_available cache hit')

    return render_template(TRENDING_TEMPLATE, trending_fee=trending_fee,
                           trending_available=trending_available)


@app.route('/watchlist', methods=['GET', 'POST'])
@login_required
@view_logger
def watch_list():
    """Watchlist handler"""

    # If the user added or removed symbols from their
    # watchlist make the changes then re-render the watchlist
    if request.method == 'POST':
        symbols = request.form['symbols'].replace(' ', '').split(',')
        symbols_to_remove = request.form['remove-symbols'].replace(' ', '').split(',')
        if symbols != ['']:

            # Insertion/deletion method returns two lists - symbols added, and symbols
            # that failed to be added. Render some user feedback with flashed messages
            symbols_added, symbols_failed_to_be_added = stock_loan.\
                insert_watchlist(current_user.id, symbols)
            if symbols_added:
                for symbol in symbols_added:
                    flash("Added {} to your watchlist".format(symbol))
            if symbols_failed_to_be_added:
                for symbol in symbols_failed_to_be_added:
                    flash("Failed to add {} to your watchlist".format(symbol))

        if symbols_to_remove != ['']:
            symbols_removed = stock_loan.\
                remove_watchlist(current_user.id, symbols_to_remove)
            if symbols_removed:
                for symbol in symbols_removed:
                    flash("Removed {} from your watchlist".format(symbol))

    # Get user's watchlist summary
    watchlist = stock_loan.get_watchlist(current_user.id)
    summary = stock_loan.summary_report(watchlist)

    print('Rendering watchlist for user: {}'.format(current_user.username))

    return render_template(WATCH_LIST_TEMPLATE, summary=summary)


@app.route('/watchlist/add/<symbol>', methods=['GET'])
@login_required
def add_to_watchlist(symbol):
    symbols_added, symbols_failed_to_be_added = stock_loan.\
        insert_watchlist(current_user.id, [symbol])
    if symbols_added:
        for symbol_added in symbols_added:
            flash("Added {} to your watchlist".format(symbol_added))
            if symbols_failed_to_be_added:
                for symbol_failed in symbols_failed_to_be_added:
                    flash("Failed to add {} to your watchlist".format(symbol_failed))

    return redirect(url_for('watch_list'))


@app.route('/watchlist/remove/<symbol>', methods=['GET'])
@login_required
def remove_from_watchlist(symbol):
    symbols_removed = stock_loan.remove_watchlist(current_user.id, [symbol])
    if symbols_removed:
        for symbol_removed in symbols_removed:
            flash("Removed {} from your watchlist".format(symbol_removed))
    else:
        flash("Failed to remove {} from your watchlist".format(symbol))

    return redirect(url_for('watch_list'))


@app.route('/historical_report', methods=['GET'])
@view_logger
@limiter.limit("60 per hour")
@limiter.limit("10 per minute")
def historical_report():
    """Historical report handler, uses url arguments to determine the symbol to report
    on and the time period (last few days every 15mins or daily long-term)"""

    # Grab the symbol and real-time flag form the url
    symbol = str(request.args['symbol'].replace(' ', '').upper())
    real_time = True if request.args['real_time'] == 'True' else False

    summary = []
    name = ''

    # Get the company name and a report based on the url parameters.
    # Check the memcache first for both. If they are not there,
    # go to the db and update the cache
    if symbol:
        summary = historical_report_cache(symbol=symbol, real_time=real_time)

        name = mc.get(symbol)
        if not name:
            print('cache miss on ' + symbol)
            name = stock_loan.get_company_name(symbol)
            if name:
                mc.set(symbol, name)

        if current_user.is_authenticated:
            stock_loan.search(symbol=symbol, userid=current_user.id)
        else:
            stock_loan.search(symbol=symbol)

        if not summary:
            flash(symbol + ' not found')
            flash('For Canadian stocks use a .CA suffix. '
                  'For other countries check the FAQ.')

    return render_template(HISTORICAL_REPORT_TEMPLATE, symbol=symbol, name=name,
                           summary=summary, real_time=real_time)


@app.route('/name_search', methods=['GET'])
@view_logger
def name_search():
    """Handler for searching the database by name"""
    try:
        name = request.args['name']
        print(name)
        name = ''.join(c for c in name if (c.isalnum() or c == ' '))
    except:
        name = ''

    summary = []

    if name:
        summary = stock_loan.name_search(name)

    return render_template(NAME_SEARCH_TEMPLATE, summary=summary, name=name)


@app.route('/filter_db', methods=['GET', 'POST'])
@view_logger
def filter_db():
    """Handler for the filter_db page"""
    form = FilterForm(request.form)
    if request.method == 'POST' and form.validate():
        summary = stock_loan.filter_db(min_available=form.min_available.data,
                                       max_available=form.max_available.data,
                                       min_fee=form.min_fee.data,
                                       max_fee=form.max_fee.data,
                                       country=form.country.data,
                                       order_by=form.order_by.data)
        if len(summary) == 100:
            flash('Results capped at 100')
        else:
            flash('Found {} results'.format(len(summary)))
        return render_template(FILTER_TEMPLATE, form=form, summary=summary)
    else:
        return render_template(FILTER_TEMPLATE, form=form, summary=[])


@app.route('/change_morning_email')
@login_required
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


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
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


@app.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    """Change email handler"""
    form = ChangeEmailForm(request.form)
    if request.method == 'POST' and form.validate():
        if current_user.check_password(form.password.data):
            current_user.email = form.new_email.data
            db.session.add(current_user)
            db.session.commit()
            flash('Email changed to {}'.format(form.new_email.data))
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
            user = User(form.username.data, form.password.data, form.email.data,
                        form.receive_emails.data)
            db.session.add(user)
            db.session.commit()
            flash('User successfully registered')
            return redirect(url_for('login'))

    else:
        return render_template(REGISTER_TEMPLATE, form=form)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("30 per hour")
@limiter.limit("10 per minute")
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

    flash('Welcome {}!'.format(user.username))
    print('User: {} logged in'.format(user.username))
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
