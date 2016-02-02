from flask import request, jsonify
from flask_jwt import current_identity, jwt_required

from . import app, login_manager, db, stock_loan, mc
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

@app.route('/api/watchlist', methods=['GET'])
@jwt_required()
def test_watchlist():
    """Watchlist endpoint"""
    print(current_identity)
    watchlist = stock_loan.get_watchlist(current_identity.id)
    return jsonify(watchlist=stock_loan.summary_report(watchlist))