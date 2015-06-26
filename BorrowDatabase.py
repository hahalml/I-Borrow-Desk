import csv
import psycopg2
from timed_function import timer
from ftplib import FTP
import time
import re
import os

DOWNLOAD_DIRECTORY = 'downloads/'

class BorrowDatabase():
    """Class for interacting with Interactive Broker's borrow database"""

    def __init__(self, database_name = 'stock_loan', filename = 'usa', create_new = False):
        """Initialize, unless create_new is True the stocks database won't be initialize.
        However, currently the class requires the proper database to be previously created"""
        self.database_name = database_name
        self.filename = filename
        self.download_directory = DOWNLOAD_DIRECTORY

        db, cursor = self._connect()
        db.close()

        if create_new:
            self._initialize_dbase()


    def update(self):
        """Connect to the IB ftp server and download the latest usa.txt file
        Write to disk a filename based on the current GMT time and use that file
        to update the borrow database"""
        time_stamp = time.strftime('%Y-%m-%d %H %M %S', time.gmtime())
        write_filename = self.download_directory + self.filename + ' ' + time_stamp + '.txt'

        connection = FTP('ftp3.interactivebrokers.com', 'shortstock')
        connection.retrbinary('RETR usa.txt', open(write_filename, 'wb').write)
        self._update_borrow(write_filename)


    def _connect(self):
        """Connect to the PostgreSQL database.  Returns a database connection. Default database is 'stock_loan' """
        try:
            db = psycopg2.connect("dbname={}".format(self.database_name))
            cursor = db.cursor()
            return db, cursor
        except:
            print("Could not find the %s database." % self.database_name)


    @timer
    def _initialize_dbase(self):
        """Just used to initialize the stocks database"""
        rows = []
        with open(self.filename + '.txt', 'rb') as csvfile:
            stockreader = csv.reader(csvfile, delimiter='|')
            for row in stockreader:
                rows.append(row)

        rows = rows[2:]

        db, cursor = self._connect()

        for row in rows:
            try:
                SQL, data = self._insert_stocks(row)
                cursor.execute(SQL, data)
                db.commit()
            except IndexError:
                print 'Index error caught'

        db.close()


    @timer
    def _update_borrow(self, filename):
        """update the borrow database - takes a filename as argument"""
        rows = []
        with open(filename, 'rb') as csvfile:
            stockreader = csv.reader(csvfile, delimiter='|')
            for row in stockreader:
                rows.append(row)

        date = rows[0][1].replace('.', '-')
        time = rows[0][2]
        datetime = ' '.join((date, time))
        print datetime

        # Cut off the first two rows that don't contain stock data
        rows = rows[2:]

        db, cursor = self._connect()
        query = ''
        errors_caught = 0
        for row in rows:
            try:
                SQL, data = self._insert_borrow(row, datetime)
                cursor.execute(SQL, data)
                db.commit()

            # Going to happen at end of file
            except IndexError:
                print 'Index error caught'

            # Will occur when a new stock appears in the database. roll back any pending transactions
            # Insert the stock into the stocks database then insert into borrow database
            except psycopg2.IntegrityError:
                print 'Integrity error caught, rolling back'
                print 'Hit cusip ' + row[3]
                db.rollback()
                SQL, data = self._insert_stocks(row)
                cursor.execute(SQL, data)
                db.commit()

                SQL, data = self._insert_borrow(row, datetime)
                cursor.execute(SQL, data)
                db.commit()
                errors_caught += 1

            except psycopg2.InternalError:
                print 'Internal Error caught'
                errors_caught += 1


        print 'Caught ', errors_caught, ' errors.'
        db.close()


    def _insert_stocks(self, row):
        """Returns SQL string and data tuple for use in a row insertion to the stocks table"""
        cusip = row[3]
        symbol = row[0]
        name = row[2]
        SQL = "INSERT INTO stocks (cusip, symbol, name) VALUES (%s, %s, %s);"
        data = (cusip, symbol, name,)
        return SQL, data


    def _insert_borrow(self, row, datetime):
        """Returns SQL string and data tuple for use in a row insertion to the borrow table"""
        cusip = row[3]
        # Replace NA rebates and fees with nonsensical dummy values
        rebate = row[5].replace('NA', '99')
        fee = row[6].replace('NA', '-99')

        # Ignore '>' symbol
        available = row[7].replace('>', '')

        SQL = "INSERT INTO borrow (datetime, cusip, rebate, fee, available) VALUES (%s, %s, %s, %s, %s);"
        data = (datetime, cusip, rebate, fee, available,)
        return SQL, data


    def insert_watchlist(self, userid, symbols):
        """Takes a userid and list of symbols, adds them to the watchlist database"""

        # Sanitize symbols
        safe_symbols = []
        for symbol in symbols:
            if self._check_symbol(symbol):
                safe_symbols.append(symbol.upper())


        # Make sure only new symbols to the user's wishlist will be added
        if safe_symbols is not None:
            safe_symbols = tuple(set(safe_symbols) - set(self.get_watchlist(userid)),)

        if safe_symbols:
            # Get the cuips from the symbol list
            cusips = []
            db, cursor = self._connect()
            SQL = "SELECT cusip FROM stocks WHERE symbol IN %s;"
            cursor.execute(SQL, [safe_symbols])
            cusips = cursor.fetchall()

            # Insert the cusips and userid into the watchlist
            for cusip in cusips:
                SQL = "INSERT INTO watchlist(userid, cusip) VALUES (%s, %s);"
                data = (userid, cusip[0],)
                cursor.execute(SQL, data)
                db.commit()

            db.close()

        # Get an updated watchlist for the user and return it
        return self.get_watchlist(userid)

    def remove_watchlist(self, userid, symbols):
        """Takes a userid and list of symbols, removes them from the watchlist database"""

        # Sanitize symbols
        safe_symbols = []
        for symbol in symbols:
            if self._check_symbol(symbol):
                safe_symbols.append(symbol.upper())


        # Make sure symbols to be removed are on the user's wishlist
        current_watchlist = self.get_watchlist(userid)
        symbols_to_remove = []
        for symbol in safe_symbols:
            if symbol in current_watchlist:
                symbols_to_remove.append(symbol)

        if symbols_to_remove:
            db, cursor = self._connect()
            SQL = "SELECT cusip FROM stocks WHERE symbol = ANY(%s);"

            cursor.execute(SQL, (symbols_to_remove,))
            cusips = cursor.fetchall()

            # Remove the cusips and userid from the watchlist
            for cusip in cusips:
                SQL = "DELETE FROM watchlist WHERE userid = %s AND cusip = %s;"
                data = (userid, cusip[0],)
                cursor.execute(SQL, data)

            db.commit()
            db.close()

        return None


    def get_watchlist(self, userid):
        """Get a list of stocks that a user has on his/her watchlist"""

        db, cursor = self._connect()
        SQL = "SELECT cusip FROM watchlist WHERE userid = %s;"
        data = (userid,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()

        SQL = "SELECT symbol FROM stocks WHERE cusip = ANY(%s);"
        data = (results,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()

        watchlist = []
        for result in results:
            watchlist.append(result[0])
        db.close()
        return watchlist


    def create_user(self, username, email):
        """Returns userid of newly created user"""

        SQL = "INSERT INTO users (username, email) VALUES (%s, %s);"
        data = (username, email)
        db, cursor = self._connect()
        cursor.execute(SQL, data, )
        db.commit()

        SQL = "SELECT userid FROM users WHERE username = %s;"
        data = (username,)
        cursor.execute(SQL, data)
        userid = cursor.fetchone()[0]
        db.close()
        return userid


    def get_user_id(self, email):
        """Get the user id given an email"""
        SQL = "SELECT userid FROM users WHERE email = %s;"
        data = (email,)
        db, cursor = self._connect()
        cursor.execute(SQL, data)

        try:
            userid = cursor.fetchone()[0]
            db.close()
            return userid
        except TypeError:
            db.close()
            return None

    def get_all_users(self):
        """Return a list of user ids, usernames, email addresses"""
        SQL = "SELECT * FROM users;"
        db, cursor = self._connect()
        cursor.execute(SQL)
        results = []
        try:
            results = cursor.fetchall()
            db.close()
        except TypeError:
            db.close()
            return None

        user_ids = []
        for row in results:
            user_ids.append(row)

        return user_ids


    @timer
    def tight_borrow(self, available=5000):
        db, cursor =self._connect()
        SQL = "SELECT symbol, available FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip) WHERE available < %s;"
        data = (available,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()
        db.close()
        return results

    @timer
    def summary_report(self, symbols):
        """Return a list of symbols and latest rebate, fee, availablity, and date/time of last update"""

        safe_symbols = []
        for symbol in symbols:
            if self._check_symbol(symbol):
                safe_symbols.append(symbol)

        db, cursor = self._connect()

        SQL = """SELECT symbol, rebate, fee, available, datetime FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip)
                WHERE symbol = ANY(%s)
                AND datetime = (SELECT max(datetime) FROM borrow)
                ORDER BY symbol;"""
        data = (safe_symbols,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()
        db.close()

        return results

    @timer
    def historical_report(self, symbol, interval = '1 HOUR'):
        """Return historical report of rebate, fee, availability for a given symbol at the given interval along with
        the Company name"""
        if self._check_symbol(symbol):
            safe_symbol = symbol.upper()
        else:
            return None, None

        db, cursor = self._connect()
        SQL = """SELECT rebate, fee, available, datetime FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip)
                WHERE symbol = %s
                ORDER BY datetime DESC;"""
        data = (safe_symbol,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()

        # If the search didn't find anything return None, None
        if results != []:
            SQL = """SELECT name FROM stocks WHERE symbol = %s;"""
            cursor.execute(SQL, data)
            name = cursor.fetchone()[0]
            db.close()
            return name, results
        else:
            return None, None


    def _check_symbol(self, text):
        """Ensure a symbol is safe for the database
        :rtype : Boolean
        """
        if re.match("^[a-zA-Z]{1,4}$", text) is not None:
            return True
        else:
            return False
