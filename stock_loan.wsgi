#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/cameron/stock_loan")

from stock_loan import app as application
application.secret_key = 'Add your secret key'