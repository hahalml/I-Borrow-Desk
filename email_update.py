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

from BorrowDatabase import BorrowDatabase

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

sub = 'Test subject to '

for user in users:
    print user
    msg = email.MIMEMultipart.MIMEMultipart()
    msg['From'] = 'Iborrow Desk'
    msg['To'] = user[2]
    msg['Subject'] = sub
    watchlist = stockLoan.get_watchlist(user[0])
    report = stockLoan.summary_report(watchlist)
    report = str(report)
    msg.attach(MIMEText(report, 'plain'))
    msg.attach(MIMEText('nsent via python', 'plain'))
    server.sendmail(username,user[2],msg.as_string())

server.quit()
