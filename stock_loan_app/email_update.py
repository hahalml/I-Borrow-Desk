__author__ = 'Cameron'
#
# Script to run every morning to send out email updates of watch lists
#
# http://www.jayrambhia.com/blog/send-emails-using-python/
import smtplib
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import jinja2

dirname, filename = os.path.split(os.path.abspath(__file__))

TEMPLATE_DIR = dirname + '/templates'
EMAIL_TEMPLATE = 'email_template.html'

# Set up jinja templates. Look for templates in the TEMPLATE_DIR
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))


def send_emails(users, stockLoan):
    """Takes a list of users and a BorrowDatabase instance and sends out emails with each user's watchlist"""

    # Grab the account password and set username
    with open(dirname + '/account.txt', 'rb') as fp:
        password = fp.read()
    username = 'iborrowdesk'
    fromaddr = 'iborrowdesk@gmail.com'

    # Connect to the gmail account
    server = smtplib.SMTP()
    server.connect(host='smtp.gmail.com', port=587)  # for eg. host = 'smtp.gmail.com', port = 587
    server.ehlo()
    server.starttls()
    server.login(username, password)

    # For each user get their watchlist summary, build the email template and send
    for user in users:
        watchlist = stockLoan.get_watchlist(user.id)
        summary = stockLoan.summary_report(watchlist)
        html = env.get_template(EMAIL_TEMPLATE).render(summary=summary, user_name=user.username)

        sub = 'Morning email update for ' + user.username

        msg = MIMEMultipart()
        msg['From'] = 'Iborrow Desk'
        msg['To'] = user.email
        msg['Subject'] = sub

        msg.attach(MIMEText(html, 'html'))
        server.sendmail(username, user.email, msg.as_string())

    server.quit()
