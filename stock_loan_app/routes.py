import os
import json

from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from apscheduler.schedulers.background import BackgroundScheduler

from stock_loan_app import app, login_manager
from models import User
from BorrowDatabase import BorrowDatabase
from email_update import send_emails

dirname, filename = os.path.split(os.path.abspath(__file__))
CLIENT_ID = json.loads(open(dirname + '/client_secrets.json', 'r').read())['web']['client_id']

# TEMPLATES
REGISTER_TEMPLATE = 'register_template.html'
LOGIN_TEMPLATE = 'login_template.html'
MAIN_PAGE_TEMPLATE = 'mainpage_template.html'
WATCH_LIST_TEMPLATE = 'watch_list_template.html'
HISTORICAL_REPORT_TEMPLATE = 'historical_report_template.html'

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'GET':
        return render_template(REGISTER_TEMPLATE)
    user = User(request.form['username'], request.form['password'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully register')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template(LOGIN_TEMPLATE)

    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash('Invalid username')
        return redirect(url_for('login'))
    if user.check_password(password) == False:
        flash('Invalid password')
        return redirect(url_for('login'))

    login_user(user)
    flash('Welcome %s!' %user.username)
    return redirect(url_for('watch_list'))

@app.route('/logout')
def logout():
    """Logs the user out"""
    logout_user()
    flash('Successfully logged out')
    return redirect(url_for('main_page'))


@app.route('/')
def main_page():
    """Mainpage hanlder"""
    return render_template(MAIN_PAGE_TEMPLATE)


@app.route('/watchlist', methods=['GET', 'POST'])
@login_required
def watch_list():
    """Watchlist handler"""

    if request.method == 'POST':
        symbols = request.form['symbols'].replace(' ', '').split(',')
        symbols_to_remove = request.form['remove-symbols'].replace(' ', '').split(',')
        if symbols != ['']:
            stockLoan.insert_watchlist(current_user.id, symbols)
        if symbols_to_remove != ['']:
            stockLoan.remove_watchlist(current_user.id, symbols_to_remove)

    # Get user's watchlist summary
    watchlist = stockLoan.get_watchlist(current_user.id)
    summary = stockLoan.summary_report(watchlist)

    return render_template(WATCH_LIST_TEMPLATE, summary=summary)


@app.route('/historical_report', methods=['GET'])
def historical_report():
    """Historical report handler"""

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
        name, summary = stockLoan.historical_report(symbol, real_time)

    return render_template(HISTORICAL_REPORT_TEMPLATE, symbol=symbol, name=name, summary=summary)


@app.before_first_request
def initialize():
    apsched = BackgroundScheduler()
    apsched.start()
    apsched.add_job(email_job, 'cron', day_of_week='mon-fri', hour=9, minute=5, timezone = 'America/New_York')


def email_job():
    """Helper function for scheduled email sender function"""
    users = User.query.filter_by(receive_email = True).all()
    send_emails(users, stockLoan)


# Create a BorrowDatabase instance
stockLoan = BorrowDatabase(database_name='stock_loan', filename='usa', create_new=False)
#
#
# # # # Program launcher - in debug mode
# if __name__ == '__main__':
#     app.secret_key = 'super_secret_key'
#     app.debug = True
#     app.run(host='0.0.0.0', port=8000)
