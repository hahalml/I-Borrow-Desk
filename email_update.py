__author__ = 'Cameron'
#
# Script to run every morning to send out email updates of watch lists
#


# http://www.jayrambhia.com/blog/send-emails-using-python/
import smtplib
import email
import os
from email.MIMEMultipart import MIMEMultipart
from email.Utils import COMMASPACE
from email.MIMEBase import MIMEBase
from email.parser import Parser
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
import mimetypes

import jinja2

from BorrowDatabase import BorrowDatabase

TEMPLATE_DIR  = 'templates'
EMAIL_TEMPLATE = 'email_template.html'

# Set up jinja templates. Look for templates in the TEMPLATE_DIR
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))




with open('account.txt', 'rb') as fp:
    password = fp.read()
username = 'iborrowdesk'

server = smtplib.SMTP()
server.connect(host='smtp.gmail.com', port=587) # for eg. host = 'smtp.gmail.com', port = 587
server.ehlo()
server.starttls()
server.login(username, password)

fromaddr = 'iborrowdesk@gmail.com'

stockLoan = BorrowDatabase()
users = stockLoan.get_all_users()



for user in users:
    print user
    user_id = user[0]
    user_name = user[1]
    user_email = user[2]
    watchlist = stockLoan.get_watchlist(user_id)
    summary = stockLoan.summary_report(watchlist)
    html = env.get_template(EMAIL_TEMPLATE).render(summary=summary, user_name = user_name)

    sub = 'Morning email update for ' + user_name

    msg = MIMEMultipart()
    msg['From'] = 'Iborrow Desk'
    msg['To'] = user_email
    msg['Subject'] = sub

    msg.attach(MIMEText(html, 'html'))
    server.sendmail(username,user_email,msg.as_string())

server.quit()
