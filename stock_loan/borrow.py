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

# Dictionary for mapping filenames (countries) to suffixes for symbols (ie; HCG.CA)
COUNTRY_CODE = {
                'australia': '.AU',
                'austria':   '.AV',
                'belgium':   '.BB',
                'british':   '.LN',
                'canada':    '.CA',
                'dutch':     '.NA',
                'france':    '.FP',
                'germany':   '.GR',
                'hongkong':  '.HK',
                'india':     '.IN',
                'italy':     '.IM',
                'japan':     '.JP',
                'mexico':    '.MM',
                'spain':     '.SM',
                'swedish':   '.SS',
                'swiss':     '.SW',
                'usa':       ''
}

class Borrow:
    """Class for interacting with Interactive Broker's Borrow database"""

    def __init__(self, database_name='stock_loan', file_names=('australia', 'austria', 'belgium', 'british',
                                                              'canada', 'dutch', 'france', 'germany', 'hongkong',
                                                              'india', 'italy', 'japan', 'mexico', 'spain', 'swedish',
                                                              'swiss', 'usa'),
                                                                create_new=False):
        """Initialize, unless create_new is True the stocks database won't be initialize.
        However, currently the class requires the proper database to be previously created"""
        self.database_name = database_name


        # Check all the passed in file names against the dictionary of allowed ones, append valid ones to
        # class variable which will keep track
        self.file_names = []
        for file in file_names:
            if file in COUNTRY_CODE:
                self.file_names.append(file)

        self.download_directory = DOWNLOAD_DIRECTORY

        # use for cacheing watchlists
        self._last_updated = datetime.min
        self._cache = {}
        self._last_cached = datetime.min

        self.all_symbols = []
        self.latest_symbols = []

        # update symbols tracked
        self._all_symbols()
        self._latest_all_symbols()

        # set count variables
        self.all_symbols_count = len(self.all_symbols)
        self.latest_symbols_count = len(self.latest_symbols)

    def _update_cache(self):
        """Puts a summary report(dict) for every symbol in the database into a cache
        key: symbol, values: summary report dictionary"""

        db, cursor = self._connect()

        SQL = "SELECT symbol FROM stocks;"
        cursor.execute(SQL)
        symbols = cursor.fetchall()
        db.close()
        self._last_cached = datetime.now()

        # Cache is a summary report dict of every symbol most recently updated
        self._cache = self._summary_report_dict(symbols)


    def _get_cache(self, symbols):
        """Takes a list of symbols and returns a summary report using data from the cache"""

        results = {}
        for symbol in symbols:
            if symbol in self._cache:
                results[symbol] = self._cache[symbol]
            else:
                results[symbol] = {'symbol': symbol, 'available': 0, 'fee': -99, 'rebate': 99, 'datetime': datetime.min, 'name': 'NA', 'country': 'NA'}

        return results

    @timer
    def update(self, files_to_download = [], update_all = True):
        """Connect to the IB ftp server and download the latest files
        Write to disk a filename based on the current GMT time and use that file
        to update the Borrow database"""

        # Get the files and filenames. Default is to just get them all (update_all)
        write_filenames = self._download_files(files_to_download=files_to_download, update_all=update_all)

        for country, filename in write_filenames.iteritems():
            # Update the borrow database
            self._update_borrow(country, filename)

        self._last_updated = datetime.now()
        self._update_cache()
        self._last_cached = datetime.now()

        # update symbol lists
        self._all_symbols()
        self._latest_all_symbols()

        # set count variables
        self.all_symbols_count = len(self.all_symbols)
        self.latest_symbols_count = len(self.latest_symbols)

    def _download_files(self, files_to_download, update_all):
        """Private function to connect to ftp and download required files. Returns a list of written files"""
        connection = FTP('ftp3.interactivebrokers.com', 'shortstock')

        # Dictionary, keys are country names, values are the actual filenames written
        write_filenames = {}

        # If update_all is set to True, just hit all the files that the database is tracking.
        # Otherwise use the parameter passed in - do a check first that it's not empty
        if update_all:
            files_to_download = self.file_names
        else:
            if files_to_download == []:
                raise ValueError('update_all flag set to false but no files to download indicated')

        for country in files_to_download:
            time_stamp = time.strftime('%Y-%m-%d %H %M %S', time.gmtime())
            read_command = 'RETR ' + country + '.txt'
            write_filename = self.download_directory + country + ' ' + time_stamp + '.txt'
            connection.retrbinary(read_command, open(write_filename, 'wb').write)
            write_filenames[country] = write_filename

        return write_filenames


    def _connect(self):
        """Connect to the PostgreSQL database.  Returns a database connection. Default database is 'stock_loan' """
        try:
            db = psycopg2.connect(database=self.database_name, user=username, password=password)
            cursor = db.cursor()
            return db, cursor
        except:
            print("Could not find the %s database." % self.database_name)


    def _update_borrow(self, country, filename):
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

        # Cut off the first two rows that don't contain( stock data
        rows = rows[2:]

        db, cursor = self._connect()
        query = ''
        errors_caught = 0

        print filename
        print country

        if country in COUNTRY_CODE:
            suffix = COUNTRY_CODE[country]

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
                    SQL, data = self._insert_stocks(row, country, suffix)
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

        else:
            print 'FILENAME DIDNT MATCH PROPERLY'

    def _insert_stocks(self, row, country, suffix):
        """Returns SQL string and data tuple for use in a row insertion to the stocks table"""
        cusip = row[3]
        symbol = row[0] + suffix
        name = row[2]
        SQL = "INSERT INTO stocks (cusip, symbol, name, country) VALUES (%s, %s, %s, %s);"
        data = (cusip, symbol, name, country,)
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
        """Takes a userid and list of symbols, adds them to the watchlist database.
        Returns a list of symbols added, and a list of symbols failed to be added"""

        # Sanitize symbols
        safe_symbols = []
        for symbol in symbols:
            if self._check_symbol(symbol):
                safe_symbols.append(symbol.upper())

        # Make sure only new symbols to the user's wishlist will be added
        if safe_symbols is not None:
            safe_symbols = tuple(set(safe_symbols) - set(self.get_watchlist(userid)), )

        symbols_inserted = []

        if safe_symbols:
            # Get the cuips from the symbol list
            cusips = []
            db, cursor = self._connect()
            SQL = "SELECT cusip FROM stocks WHERE symbol IN %s;"
            cursor.execute(SQL, [safe_symbols])
            cusips = cursor.fetchall()

            if cusips != []:

                # Build a list of symbols that were actually inserted into the watchlist (valid ones essentially)
                SQL = "SELECT symbol FROM stocks WHERE cusip = ANY(%s)"
                cursor.execute(SQL, [cusips])
                results = cursor.fetchall()
                for row in results:
                    symbols_inserted.append(row[0])

                # Insert the cusips and userid into the watchlist
                for cusip in cusips:
                    SQL = "INSERT INTO watchlist(userid, cusip) VALUES (%s, %s);"
                    data = (userid, cusip[0],)
                    cursor.execute(SQL, data)
                    db.commit()

                db.close()

        # Return a list of symbols inserted, and a list of symbols that failed to be inserted
        symbols_not_inserted = list(set(safe_symbols) - set(symbols_inserted))

        return symbols_inserted, symbols_not_inserted

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

        symbols_removed = []

        if symbols_to_remove:
            db, cursor = self._connect()
            SQL = "SELECT cusip FROM stocks WHERE symbol = ANY(%s);"

            cursor.execute(SQL, (symbols_to_remove,))
            cusips = cursor.fetchall()

            # Build a list of symbols that were actually removed from the watchlist (valid ones essentially)
            SQL = "SELECT symbol FROM stocks WHERE cusip = ANY(%s)"
            cursor.execute(SQL, [cusips])
            results = cursor.fetchall()
            for row in results:
                symbols_removed.append(row[0])

            # Remove the cusips and userid from the watchlist
            for cusip in cusips:
                SQL = "DELETE FROM watchlist WHERE userid = %s AND cusip = %s;"
                data = (userid, cusip[0],)
                cursor.execute(SQL, data)

            db.commit()
            db.close()

        # Return a list of symbols removed
        return symbols_removed

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
    def filter(self, min_available = 0, max_available = 10000000, min_fee = 0, max_fee = 100, country = 'usa', order_by = 'symbol'):
        """General filter function. Loops over the cache testing each stock against the criteria given
        returns a maximum of 100 results"""

        country = country.lower()

        if order_by not in ['symbol', 'fee', 'available']:
            raise ValueError('Attempted to sort by an invalid field. Only symbol, fee, available allowed')

        # If the cache was last updated before the database was last updated, update the cache before
        # running the filter
        if self._last_cached <= self._last_updated:
            self._update_cache()

        results = []

        # Test every item in the cache against the criteria and append to a list.
        for stock in self._cache:
            if self._cache[stock]['country'] == country:
                if self._cache[stock]['available'] > min_available and self._cache[stock]['available'] < max_available:
                    if self._cache[stock]['fee'] > min_fee and self._cache[stock]['fee'] < max_fee:
                        results.append(self._cache[stock])

            if len(results) >= 100: break

        # Sort the list by the given key and return results
        return sorted(results, key = lambda k: k[order_by])

    @timer
    def summary_report(self, symbols):
        """Return a sorted by symbol list of dictionaries including symbols and latest rebate,
        fee, availability, and date/time of last update"""

        safe_symbols = []
        for symbol in symbols:
            if self._check_symbol(symbol) and symbol.upper() in self.all_symbols:
                safe_symbols.append(symbol.upper())

        # If the cache was last updated before the database was last updated, update the cache before
        # getting the summary report
        if self._last_cached <= self._last_updated:
            self._update_cache()

        # Get the cache
        results_dict = self._get_cache(safe_symbols)

        # Turn the cache, which is just a dictionary, into a sorted by symbol list of dictionaries for
        # Ease of use externally
        results =[]
        for item in results_dict:
            results.append(results_dict[item])
        results = sorted(results, key = lambda k: k['symbol'])

        return results


    def _summary_report_dict(self, symbols):
        """Run a database query on every symbol in the list passed in. Return a dictionary with keys as symbols
        and values as a dictionary for each field returned (including symbol)"""
        db, cursor = self._connect()

        SQL = """SELECT symbol, rebate, fee, available, datetime, name, country FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip)
                WHERE symbol = ANY(%s)
                AND datetime = (SELECT max(datetime) FROM Borrow)
                ORDER BY symbol;"""
        data = (symbols,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()
        db.close()

        dict_results = {}
        for row in results:
            dict_results[row[0]] = {'symbol': row[0], 'rebate': row[1], 'fee': row[2], 'available': row[3], 'datetime': row[4], 'name': row[5], 'country': row[6]}

        return dict_results

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
            SQL = """SELECT rebate, fee, available, datetime FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip)
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

        # If the search didn't find anything return None
        if results:
            return results
        else:
            return  None

    def get_company_name(self, symbol):
        """Returns the name of a Company given a symbol. Returns None if no symbol exists"""
        if self._check_symbol(symbol):
            safe_symbol = symbol.upper()
        else:
            return None

        data = (safe_symbol,)
        db, cursor = self._connect()

        SQL = """SELECT name FROM stocks WHERE symbol = %s;"""
        cursor.execute(SQL, data)

        try:
            name = cursor.fetchone()[0]
        except TypeError:
            print 'Symbol not found'
            return None
        db.close()
        return name



    @timer
    def _latest_all_symbols(self):
        """Set the class variable list of every symbol in the latest update from IB"""
        db, cursor = self._connect()
        SQL = """SELECT distinct symbol FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip)
                WHERE datetime = (SELECT max(datetime) FROM borrow);"""
        cursor.execute(SQL)
        results = []
        rows = cursor.fetchall()
        for row in rows:
            results.append(row[0])
        db.close()
        self.latest_symbols = results

    @timer
    def _all_symbols(self):
        """Set the list of all symbols in the database"""
        db, cursor = self._connect()
        SQL = """SELECT DISTINCT symbol FROM stocks;"""
        cursor.execute(SQL)
        results = []
        rows  = cursor.fetchall()
        for row in rows:
            results.append(row[0])
        db.close()
        self.all_symbols = results

    @timer
    def clean_dbase(self):
        """Remove entries _not_ bw 0925 and 0935 older than 1 week. Maintains historical record
        while getting rid of stale intraday data"""
        db, cursor = self._connect()
        SQL = """DELETE FROM Borrow
              WHERE cast(datetime as time) NOT BETWEEN '9:35' and '9:44'
              AND datetime < now() - interval '7days';"""

        cursor.execute(SQL)
        db.commit()
        db.close()

        return None

    def _check_symbol(self, text):
        """Ensure a symbol is safe for the database
        :rtype : Boolean
        """
        if re.match("^[\sa-zA-Z0-9\.]{1,8}$", text) is not None:
            return True
        else:
            return False
