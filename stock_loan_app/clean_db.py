# Just a script for cronjob to run every day to clean the database of stale entries
from borrow import Borrow

stock_loan = Borrow(database_name='stock_loan', filename='usa', create_new=False)
stock_loan.clean_dbase()
