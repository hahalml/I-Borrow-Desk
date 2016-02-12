from flask import request, jsonify
from flask_jwt import current_identity, jwt_required

from . import app, db, stock_loan, mc
from .models import User
from .utils import historical_report_cache


@app.route('/_json_historical_report')
def json_historical_report():
    """Handler to deliver historical report in JSON format"""

    symbol = request.args.get('symbol')
    real_time = request.args.get('real_time')

    print("AJAX request for {}".format(symbol))
    report = historical_report_cache(symbol=symbol, real_time=real_time)

    return jsonify(data=report)

@app.route('/api/ticker/<symbol>', methods=['GET'])
def test_json_historical_report(symbol):
    """Handler to deliver historical report in JSON format"""

    print("AJAX request for {}".format(symbol))
    real_time = historical_report_cache(symbol=symbol, real_time=True)
    daily = historical_report_cache(symbol=symbol, real_time=False)
    name = stock_loan.get_company_name(symbol)

    return jsonify(real_time=real_time, daily=daily, symbol=symbol, name=name)

@app.route('/api/search/<query>', methods=['GET'])
def test_json_company_search(query):
    """Handler to return possible Company names"""

    #query = ''.join(c for c in query if (c.isalnum() or c == ' '))
    if query.upper() in stock_loan.all_symbols:
        name = stock_loan.get_company_name(query)
        return jsonify(results=[{'symbol': query.upper(), 'name': name}])

    summary = stock_loan.name_search(query)
    results = [{'symbol': row.symbol, 'name': row.name} for row in summary] \
        if summary else []
    print(results)
    return jsonify(results=results)

@app.route('/api/trending', methods=['GET'])
def test_json_trending():
    """Return trending stocks"""
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
    return jsonify(available=trending_available, fee=trending_fee)

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def test_watchlist():
    """Watchlist endpoint"""
    print(current_identity)
    if request.method == 'POST':
        symbol = request.get_json()['symbol']
        stock_loan.insert_watchlist(current_identity.id, [symbol])
        print('post', symbol)
    if request.method == 'DELETE':
        symbol = request.args.get('symbol')
        stock_loan.remove_watchlist(current_identity.id, [symbol.upper()])
        print('delete', symbol)


    watchlist = stock_loan.get_watchlist(current_identity.id)
    return jsonify(watchlist=stock_loan.summary_report(watchlist))

@app.route('/api/register', methods=['POST'])
def test_register():
    data = request.get_json()
    errors = {}
    if User.query.filter_by(username=data['username']).first():
        errors['username'] = 'A User with that Username already exists'
    if User.query.filter_by(email=data['email']).first():
        errors['email'] = 'A User with that Email Address already exists'
    if errors:
        return jsonify(errors=errors), 409

    if len(data['username']) < 6:
        errors['username'] = 'Username must be at least 6 characters.'
    if len(data['password']) < 6:
        errors['password'] = 'Password must be at least 6 characters.'
    if errors:
        return jsonify(errors=errors), 406

    if data['password'] != data['confirmPassword']:
        raise ValueError

    user = User(data['username'], data['password'], data['email'], True)
    db.session.add(user)
    db.session.commit()

    return jsonify(result='{} created'.format(data['username'])), 201

@app.route('/api/user/email', methods=['POST'])
@jwt_required()
def test_change_email():
    """Change email endpoint"""
    print(current_identity)
    data = request.get_json()
    if not current_identity.check_password(data['password']):
        return jsonify(errors= {'password': 'Invalid password'}), 401
    elif User.query.filter_by(email=data['email']).first():
        return jsonify(errors={'email': 'A User with that Email Address already exists'}),\
               409
    current_identity.email = data['email']
    db.session.add(current_identity)
    db.session.commit()
    return jsonify(result='Email successfully changed')

@app.route('/api/user/morning', methods=['POST'])
@jwt_required()
def test_change_morning_email():
    """Change email endpoint"""
    print(current_identity)
    data = request.get_json()
    current_identity.receive_email = not current_identity.receive_email
    db.session.add(current_identity)
    db.session.commit()
    return jsonify(result='Morning email successfully changed')

@app.route('/api/user/password', methods=['POST'])
@jwt_required()
def test_change_password():
    """Change password endpoint"""
    print(current_identity)
    data = request.get_json()
    if not current_identity.check_password(data['password']):
        return jsonify(errors={'password': 'Invalid password'}), 401
    elif data['newPassword'] != data['confirmPassword']:
        return jsonify(errors={'confirmPassword': 'Passwords must match'}), 401

    current_identity.set_password(data['newPassword'])
    db.session.add(current_identity)
    db.session.commit()
    return jsonify(result='Password successfully changed')


@app.route('/api/user', methods=['GET'])
@jwt_required()
def test_get_profile():
    """Get username"""
    print(current_identity, 'In get user endpoint')
    return jsonify({'username': current_identity.username,
                    'receiveEmail': current_identity.receive_email})

@app.route('/api/filter', methods=['GET'])
def test_filter():
    try:
        summary = stock_loan.filter_db(**dict(request.args.items()))
    except TypeError:
        return jsonify(error='Invalid filter'), 400
    capped = len(summary) == 100
    return jsonify(results=summary, capped=capped)

@app.route('/api/filter/most_expensive', methods=['GET'])
def test_most_expensive():
    summary = mc.get('mainpage')
    if not summary:
        summary = stock_loan.filter_db(min_available=10000, min_fee=20, order_by='fee')
        summary = summary[:20]
        mc.set('mainpage', summary)
        print('mainpage cache miss')
    else:
        print('mainpage cache hit')

    return jsonify(results=summary)