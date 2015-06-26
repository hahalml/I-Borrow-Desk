
# Just a script for cronjob to run every during trading hours to update the database
import time
from BorrowDatabase import BorrowDatabase

# Sleep 5 seconds (enough time to grab the FTP files at 3s past the hour)
time.sleep(5)

stockLoan = BorrowDatabase(database_name='stock_loan', filename='usa', create_new=False)
stockLoan.update()