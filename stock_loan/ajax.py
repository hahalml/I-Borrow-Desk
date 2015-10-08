from flask import request, jsonify
from . import app, login_manager, db, stock_loan, mc
from .utils import historical_report_cache

@app.route('/_json_historical_report')
def json_historical_report():
    """Handler to deliver historical report in JSON format"""

    symbol = request.args.get('symbol')
    real_time = request.args.get('real_time')

    print("AJAX request for {}".format(symbol))
    report = historical_report_cache(symbol=symbol, real_time=False)


    return jsonify(data=report)