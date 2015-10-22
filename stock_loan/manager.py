from apscheduler.schedulers.blocking import BlockingScheduler
import memcache
from borrow import Borrow

def update_database_all():
    """Helper function for updating the entire database"""
    # Update the db
    stock_loan.update()
    # Clear the cache
    mc.flush_all()


def update_database_north_america():
    """Helper function for updating the North American files"""
    # Update the db
    stock_loan.update(files_to_download=['usa', 'canada', 'mexico'], update_all=False)
    # Clear the cache
    mc.flush_all()


def update_database_europe():
    """Helper function for updating the European files"""
    # Update the db
    stock_loan.update(files_to_download=['austria', 'belgium', 'british', 'dutch', 'france', 'germany', 'italy',
                                         'spain', 'swedish', 'swiss'], update_all=False)
    # Clear the cache
    mc.flush_all()


def update_database_asia():
    """Helper function for updating the European files"""
    # Update the db
    stock_loan.update(files_to_download=['australia', 'hongkong', 'india', 'japan'], update_all=False)
    # Clear the cache
    mc.flush_all()

def clean_db():
    """Helper function for cleaning the database"""
    stock_loan.clean_dbase()

# Perform scheduled updates to the Borrow DB
if __name__ == '__main__':
    # Use blocking scheduler as this is run as a daemon
    apsched = BlockingScheduler()
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    stock_loan = Borrow()

    # Add a job for updating the entire database (940am weekdays EST to be stored for historical reports -
    # won't collide with other updates)
    apsched.add_job(update_database_all, 'cron', day_of_week='mon-fri', minute='40', hour='9',
                    timezone='America/New_York')

    # Add a job for cleaning the database
    apsched.add_job(clean_db, 'cron', day_of_week='mon-fri', minute='5', hour='0', timezone='America/New_York')

    # Add jobs for each region so database is updated roughly in line with market hours
    apsched.add_job(update_database_north_america, 'cron', day_of_week='mon-fri', minute='3-48/15', hour='8-17',
                    timezone='America/New_York')

    apsched.add_job(update_database_europe, 'cron', day_of_week='mon-fri', minute='3-48/15', hour='8-17',
                    timezone='UTC')

    apsched.add_job(update_database_asia, 'cron', day_of_week='mon-fri', minute='3-48/15', hour='0-10',
                    timezone='UTC')

    apsched.start()