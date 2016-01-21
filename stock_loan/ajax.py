from flask import request, jsonify
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

@app.route('/api/company/<name>', methods=['GET'])
def test_json_company_search(name):
    """Handler to return possible Company names"""

    name = ''.join(c for c in name if (c.isalnum() or c == ' '))

    summary = stock_loan.name_search(name)

    return jsonify(results=summary)