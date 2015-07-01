__author__ = 'Cameron'


# Just a script for cronjob to run every day to clean the database of stale entries
from BorrowDatabase import BorrowDatabase

stockLoan = BorrowDatabase(database_name='stock_loan', filename='usa', create_new=False)
stockLoan.clean_dbase()