
# Just a script for cronjob to run every during trading hours to update the database
from BorrowDatabase import BorrowDatabase

stockLoan = BorrowDatabase(database_name='stock_loan', filename='usa', create_new=False)
stockLoan.update()