from . import mc
from . import stock_loan, db
from functools import wraps
from flask.ext.login import current_user


def historical_report_cache(*, symbol, real_time):
    """Return the historical report for a given symbol and real_time flag. Takes care of memcache"""
    print('Running historical report on ' + symbol)

    key_summary = str(symbol + str(real_time))
    summary = mc.get(key_summary)

    if not summary:
        print('cache miss on ' + key_summary)
        summary = stock_loan.historical_report(symbol, real_time)
        if summary:
            mc.set(key_summary, summary)

    return summary


def view_logger(func):
    """View decorator to track page views by logged in users"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Only track logged in users
        if not current_user.is_anonymous:
            current_user.increment_views()
            db.session.commit()
        return func(*args, **kwargs)

    return decorated_view
