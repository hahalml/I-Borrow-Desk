import random
import string
import os
import httplib2
import json
import requests
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as login_session
from flask.ext.seasurf import SeaSurf

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from BorrowDatabase import BorrowDatabase

# Create a Flask instance
app = Flask(__name__)

# Implement SeaSurf extension for preventing cross-site request forgery
csrf = SeaSurf(app)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Stock Loan App"


# TEMPLATES
LOGIN_TEMPLATE = 'login_template.html'
MAINPAGE_TEMPLATE = 'mainpage_template.html'
WATCH_LIST_TEMPLATE = 'watch_list_template.html'
HISTORICAL_REPORT_TEMPLATE = 'historical_report_template.html'


def checkLogin():
    if 'user_id' in login_session:
        return True
    else:
        return False


@app.route('/')
def mainPage():
    """Mainpage hanlder"""
    return render_template(MAINPAGE_TEMPLATE, login_session=login_session, logged_in=checkLogin())


@app.route('/watchlist', methods=['GET', 'POST'])
def watchList():
    """Watchlist handler"""

    if checkLogin() == False:
        flash('Please log in')
        return redirect(url_for('showLogin'))

    if request.method == 'POST':
        symbols = request.form['symbols'].replace(' ', '').split(',')
        symbols_to_remove = request.form['remove-symbols'].replace(' ', '').split(',')
        if symbols != ['']:
            stockLoan.insert_watchlist(login_session['user_id'], symbols)
        if symbols_to_remove != ['']:
            stockLoan.remove_watchlist(login_session['user_id'], symbols_to_remove)

    # Get user's watchlist summary
    watchlist = stockLoan.get_watchlist(login_session['user_id'])
    summary = stockLoan.summary_report(watchlist)

    return render_template(WATCH_LIST_TEMPLATE, summary=summary, login_session=login_session, logged_in=True)

@app.route('/historical_report/', methods=['GET', 'POST'])
@app.route('/historical_report/<string:symbol>', methods=['GET', 'POST'])
def historical_report(symbol = ''):
    """Historical report handler"""

    logged_in = checkLogin()

    summary = []
    name = ''
    if request.method == 'POST':
        symbol = request.form['symbol'].replace(' ', '').split(',')[0]
        if symbol:
            name, summary = stockLoan.historical_report(symbol)
    else:
        if symbol:
            name, summary = stockLoan.historical_report(symbol)

    return render_template(HISTORICAL_REPORT_TEMPLATE, name=name, summary=summary, login_session=login_session,
                           logged_in=logged_in)


@app.route('/login')
def showLogin():
    """Login page handler"""
    # antiforgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template(LOGIN_TEMPLATE, STATE=state, login_session=login_session)


# Couldn't figure out how to include the cookie in the AJAX request so exempted it from
# the CSRF. Protect add/edit/delete however
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Slighly modified from Udacity course. Uses OAuth 2 Google ID login"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = stockLoan.get_user_id(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    return stockLoan.create_user(login_session['username'], login_session['email'])


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gDisconnect():
    """Slighly modified from Udacity course. Logs a user out."""

    # Only disconnect a connected user.
    # Try-except structure to account for deleted cookies
    try:
        credentials = json.loads(login_session.get('credentials'))
    except TypeError:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['state']
        del login_session['provider']

        flash('Successfully disconnected.')
        return redirect(url_for('mainPage'))

    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'

        return response

# Create a BorrowDatabase instance
stockLoan = BorrowDatabase(database_name='stock_loan', filename='usa', create_new=False)



#
#
# # # Program launcher - in debug mode
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
