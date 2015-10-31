# Script to run every morning to send out email updates of watch lists
#
# http://www.jayrambhia.com/blog/send-emails-using-python/
from collections import defaultdict
from decimal import *
import requests
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jinja2

dirname, filename = os.path.split(os.path.abspath(__file__))

TEMPLATE_DIR = dirname + '/templates'
EMAIL_TEMPLATE = 'email_template.html'

# Set up jinja templates. Look for templates in the TEMPLATE_DIR
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))


def send_emails(users, stockLoan):
    """Takes a list of users and a Borrow instance
        and sends out emails with each user's watchlist"""

    # Grab the account password and set username
    with open(dirname + '/account.txt', 'rb') as fp:
        password = fp.read()

    password = password.decode(encoding='UTF-8')

    username = 'iborrowdesk'

    # Connect to the gmail account
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.ehlo()
    server.starttls()
    server.login(username, password)

    # For each user get their watchlist summary, build the email template and send
    for user in users:
        watchlist = stockLoan.get_watchlist(user.id)
        summary = stockLoan.summary_report(watchlist)

        if summary:
            try:
                prices = get_prices(summary)
                print(prices)
            except ValueError:
                prices = None

            print('Running email for ', user.username)
            print(summary[0])
            html = env.get_template(EMAIL_TEMPLATE).render(summary=summary,
                                                           prices=prices,
                                                           user_name=user.username)

            sub = 'Morning email update for ' + user.username

            msg = MIMEMultipart()
            msg['From'] = 'Iborrow Desk'
            msg['To'] = user.email
            msg['Subject'] = sub

            msg.attach(MIMEText(html, 'html'))
            server.sendmail(username, user.email, msg.as_string())
        else:
            print('Empty watchlist for ', user.username)

    server.quit()


def get_prices(summary):
    """Query Yahoo Finance and return dictionary of symbol:price pairs"""

    # Only bothering with US symbols here
    valid_symbols = [symbol.symbol for symbol in summary if symbol.country == 'usa']

    if not valid_symbols:
        raise ValueError('No valid symbols')

    # God damn this is ugly
    string_symbols = '%22'
    for symbol in valid_symbols[:-1]:
        string_symbols += symbol
        string_symbols += '%22%2C%22'
    string_symbols += valid_symbols[-1] + '%22'
    url = """https://query.yahooapis.com/v1/public/yql?q=select%20symbol%2C%20LastTrade
    PriceOnly%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(""" \
          + string_symbols + """)&format=json&env=store%3A%2F%2Fdatatables.
          org%2Falltableswithkeys&callback="""

    response = requests.get(url).json()
    prices = response['query']['results']['quote']

    results = defaultdict(Decimal)

    # Yahoo response is simply a dict if only one symbol returned, not a list
    if type(prices) == dict:
        results[prices['symbol']] = prices['LastTradePriceOnly']
        return results
    else:
        for symbol in prices:
            results[symbol['symbol']] = symbol['LastTradePriceOnly']

        return results
