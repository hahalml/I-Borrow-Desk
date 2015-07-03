import csv
from timed_function import timer
from ftplib import FTP
import time
from datetime import datetime
import re
import os
import ConfigParser

import psycopg2

dirname, file_name = os.path.split(os.path.abspath(__file__))
DOWNLOAD_DIRECTORY = dirname + '/downloads/'

# Grab database config
parser = ConfigParser.ConfigParser()
parser.read(dirname + '/database_settings.cfg')
username = parser.get('postgresql', 'username')
password = parser.get('postgresql', 'password')


class Borrow:
    """Class for interacting with Interactive Broker's Borrow database"""

    def __init__(self, database_name='stock_loan', filename='usa', create_new=False):
        """Initialize, unless create_new is True the stocks database won't be initialize.
        However, currently the class requires the proper database to be previously created"""
        self.database_name = database_name
        self.filename = filename
        self.download_directory = DOWNLOAD_DIRECTORY

        db, cursor = self._connect()
        db.close()

        if create_new:
            self._initialize_dbase()

        # use for cacheing watchlists
        self._last_updated = datetime.min
        self._cache = {}
        self._last_cached = datetime.min

    def _update_cache(self):
        """Puts a summary report for every symbol in the database into a dictionary cache
        key: symbol, values: line (including symbol) of summary report"""

        db, cursor = self._connect()

        SQL = "SELECT symbol FROM stocks;"
        cursor.execute(SQL)
        symbols = cursor.fetchall()
        db.close()
        self._last_cached = datetime.now()

        # Create a cache where the keys are symbols and the values are lines in a summary report
        results = self._summary_report_database(symbols)
        self._cache = {result[0]: result for result in results}

    def _get_cache(self, symbols):
        """Takes a list of symbols and returns a summary report using data from the cache"""

        results = []
        for symbol in symbols:
            if symbol in self._cache:
                results.append(self._cache[symbol])
            else:
                results.append([symbol, 0, 0, 0, datetime.min])

        return results

    @timer
    def update(self):
        """Connect to the IB ftp server and download the latest usa.txt file
        Write to disk a filename based on the current GMT time and use that file
        to update the Borrow database"""
        time_stamp = time.strftime('%Y-%m-%d %H %M %S', time.gmtime())
        write_filename = self.download_directory + self.filename + ' ' + time_stamp + '.txt'

        connection = FTP('ftp3.interactivebrokers.com', 'shortstock')
        connection.retrbinary('RETR usa.txt', open(write_filename, 'wb').write)

        # Update the borrow then update the cache
        self._update_borrow(write_filename)
        self._last_updated = datetime.now()
        self._update_cache()
        self._last_cached = datetime.now()

    def _connect(self):
        """Connect to the PostgreSQL database.  Returns a database connection. Default database is 'stock_loan' """
        try:
            db = psycopg2.connect(database=self.database_name, user=username, password=password)
            cursor = db.cursor()
            return db, cursor
        except:
            print("Could not find the %s database." % self.database_name)

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

    def _update_borrow(self, filename):
        """update the Borrow database - takes a filename as argument"""
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
            # Insert the stock into the stocks database then insert into Borrow database
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
        """Returns SQL string and data tuple for use in a row insertion to the Borrow table"""
        cusip = row[3]
        # Replace NA rebates and fees with nonsensical dummy values
        rebate = row[5].replace('NA', '99')
        fee = row[6].replace('NA', '-99')

        # Ignore '>' symbol
        available = row[7].replace('>', '')

        SQL = "INSERT INTO Borrow (datetime, cusip, rebate, fee, available) VALUES (%s, %s, %s, %s, %s);"
        data = (datetime, cusip, rebate, fee, available,)
        return SQL, data

    @timer
    def insert_watchlist(self, userid, symbols):
        """Takes a userid and list of symbols, adds them to the watchlist database"""

        # Sanitize symbols
        safe_symbols = []
        for symbol in symbols:
            if self._check_symbol(symbol):
                safe_symbols.append(symbol.upper())

        # Make sure only new symbols to the user's wishlist will be added
        if safe_symbols is not None:
            safe_symbols = tuple(set(safe_symbols) - set(self.get_watchlist(userid)), )

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

    @timer
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

    @timer
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

    @timer
    def tight_borrow(self, available=5000):
        db, cursor = self._connect()
        SQL = "SELECT symbol, available FROM stocks JOIN Borrow ON (stocks.cusip = Borrow.cusip) WHERE available < %s;"
        data = (available,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()
        db.close()
        return results

    @timer
    def summary_report(self, symbols):
        """Return a list of symbols and latest rebate, fee, availability, and date/time of last update"""

        safe_symbols = []
        for symbol in symbols:
            if self._check_symbol(symbol):
                safe_symbols.append(symbol)

        # If the cache was last updated before the database was last updated, update the cache before
        # getting the summary report
        if self._last_cached <= self._last_updated:
            self._update_cache()

        return self._get_cache(safe_symbols)

    def _summary_report_database(self, symbols):
        db, cursor = self._connect()

        SQL = """SELECT symbol, rebate, fee, available, datetime FROM stocks JOIN Borrow ON (stocks.cusip = Borrow.cusip)
                WHERE symbol = ANY(%s)
                AND datetime = (SELECT max(datetime) FROM Borrow)
                ORDER BY symbol;"""
        data = (symbols,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()
        db.close()

        return results

    @timer
    def historical_report(self, symbol, real_time=False):
        """Return historical report of rebate, fee, availability for a given symbol  along with the Company name
        The default interval is daily (9:30AM for the opening of the market) - if realtime flag is set to True
        the last 100 entries will be returned - about 3 days of data."""
        if self._check_symbol(symbol):
            safe_symbol = symbol.upper()
        else:
            return None, None

        db, cursor = self._connect()
        data = (safe_symbol,)

        if real_time:
            SQL = """SELECT rebate, fee, available, datetime FROM stocks JOIN Borrow ON (stocks.cusip = Borrow.cusip)
                    WHERE symbol = %s
                    ORDER BY datetime DESC;"""
        else:
            SQL = """SELECT rebate, fee, available, cast(datetime as date) as date
                    FROM stocks JOIN Borrow ON (stocks.cusip = Borrow.cusip)
                    WHERE symbol = %s
                    AND cast(datetime as time) between '9:30' and '9:40'
                    ORDER BY datetime DESC;"""

        cursor.execute(SQL, data)
        results = cursor.fetchall()

        # If the search didn't find anything return None, None
        if results:
            SQL = """SELECT name FROM stocks WHERE symbol = %s;"""
            cursor.execute(SQL, data)
            name = cursor.fetchone()[0]
            db.close()
            return name, results
        else:
            return None, None

    @timer
    def clean_dbase(self):
        """Remove entries _not_ bw 0930 and 0940 older than 1 week. Maintains historical record
        while getting rid of stale intraday data"""
        db, cursor = self._connect()
        SQL = """DELETE FROM Borrow
              WHERE cast(datetime as time) NOT BETWEEN '9:30' and '9:40'
              AND datetime < now() - interval '7days';"""

        cursor.execute(SQL)
        db.commit()
        db.close()

        return None

    def _check_symbol(self, text):
        """Ensure a symbol is safe for the database
        :rtype : Boolean
        """
        if re.match("^[a-zA-Z]{1,4}$", text) is not None:
            return True
        else:
            return False
