from __future__ import print_function
from __future__ import absolute_import
import csv
from ftplib import FTP
from datetime import datetime
import re
import os
import configparser
import time
import collections


import psycopg2
from psycopg2.extensions import AsIs

dirname, file_name = os.path.split(os.path.abspath(__file__))
DOWNLOAD_DIRECTORY = dirname + '/downloads/'

# Grab database config
parser = configparser.ConfigParser()
parser.read(dirname + '/database_settings.cfg')
username = parser.get('postgresql', 'username')
password = parser.get('postgresql', 'password')

# Dictionary for mapping filenames (countries) to suffixes for symbols (ie; HCG.CA)
COUNTRY_CODE = {
    'australia': '.AU',
    'austria': '.AV',
    'belgium': '.BB',
    'british': '.LN',
    'canada': '.CA',
    'dutch': '.NA',
    'france': '.FP',
    'germany': '.GR',
    'hongkong': '.HK',
    'india': '.IN',
    'italy': '.IM',
    'japan': '.JP',
    'mexico': '.MM',
    'spain': '.SM',
    'swedish': '.SS',
    'swiss': '.SW',
    'usa': ''
}

Stock = collections.namedtuple('Stock', ['symbol', 'rebate', 'fee', 'available', 'datetime', 'name',
                                                       'country'])

def timer(f):
    def decorated(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print(f.__name__ + ' took {} seconds'.format(te - ts))
        return result

    return decorated


class Borrow:
    """Class for interacting with Interactive Broker's Borrow database"""
    def __init__(self, database_name='stock_loan', file_names=('australia', 'austria', 'belgium', 'british',
                                                               'canada', 'dutch', 'france', 'germany', 'hongkong',
                                                               'india', 'italy', 'japan', 'mexico', 'spain', 'swedish',
                                                               'swiss', 'usa'), create_new=False):
        """Initialize, unless create_new is True the stocks database won't be initialized.
        However, currently the class requires the proper database to be previously created"""

        print("Initializing Borrow")

        self.database_name = database_name

        # Check all the passed in file names against the dictionary of allowed ones, append valid ones to
        # instance variable which will keep track
        self.file_names = []
        for file in file_names:
            if file in COUNTRY_CODE:
                self.file_names.append(file)

        self.download_directory = DOWNLOAD_DIRECTORY

        # global instance variable for tracking duplicates during updated
        self._cusips_updated = []

        self.all_symbols = []
        self.latest_symbols = []

        # update symbols tracked
        self.refresh_all_symbols()
        self.refresh_latest_all_symbols()

        # set count variables
        self.all_symbols_count = len(self.all_symbols)
        self.latest_symbols_count = len(self.latest_symbols)

        # timestamp dictionary - for avoiding duplicate imports
        self._timestamps = {country: None for country in self.file_names}

        # update trending lists
        self.update_trending()


    @timer
    def update(self, files_to_download=None, update_all=True):
        """Connect to the IB ftp server and download the latest files
        Write to disk a filename based on the current GMT time and use that file
        to update the Borrow database"""

        # Get the files and filenames. Default is to just get them all (update_all)
        write_filenames = self._download_files(files_to_download=files_to_download, update_all=update_all)

        for country, filename in write_filenames.items():
            # Update the borrow database
            self._update_borrow(country, filename)

         # Clear the cusips updated
        print(len(self._cusips_updated), ' symbols updated.')
        self._cusips_updated = []

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
            if files_to_download is None:
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
            print("Could not find the {} database.".format(self.database_name))

    def _update_borrow(self, country, filename):
        """update the Borrow database - takes a filename as argument"""
        rows = []
        with open(filename, 'r') as csvfile:
            stockreader = csv.reader(csvfile, delimiter='|')
            for row in stockreader:
                rows.append(row)

        date = rows[0][1].replace('.', '-')
        time = rows[0][2]
        datetime = ' '.join((date, time))
        print(datetime)

        # Check to make sure the file hasn't already been scraped and added to the database
        if datetime == self._timestamps[country]:
            print('Already updated this country - moving on')
            return None
        else:
            self._timestamps[country] = datetime

        # Cut off the first two rows that don't contain( stock data
        rows = rows[2:]

        db, cursor = self._connect()
        errors_caught = 0

        print(filename)
        print(country)

        if country in COUNTRY_CODE:
            suffix = COUNTRY_CODE[country]

            for row in rows:
                try:
                    # duplicate check
                    if row[3] not in self._cusips_updated:
                        SQL, data = Borrow._insert_borrow(row, datetime)
                        cursor.execute(SQL, data)
                        SQL, data = Borrow._update_stocks(row, updated=datetime)
                        cursor.execute(SQL, data)
                        self._cusips_updated.append(row[3])

                # Going to happen at end of file
                except IndexError:
                    print('Index error caught')

                # Will occur when a new stock appears in the database. roll back any pending transactions
                # Insert the stock into the stocks database then insert into Borrow database
                except psycopg2.IntegrityError:
                    print('Integrity error caught, rolling back')
                    print('Hit cusip ' + row[3])
                    db.rollback()
                    SQL, data = Borrow._insert_stocks(row, country, suffix, updated=datetime)
                    cursor.execute(SQL, data)

                    SQL, data = Borrow._insert_borrow(row, datetime)
                    cursor.execute(SQL, data)
                    errors_caught += 1

                except psycopg2.InternalError:
                    print('Internal Error caught')
                    errors_caught += 1

                db.commit()

            print('Caught ', errors_caught, ' errors.')
            db.close()

        else:
            print('FILENAME DIDNT MATCH PROPERLY')

    ### SQL GENERATORS
    @staticmethod
    def _insert_stocks(row, country, suffix, updated):
        """Returns SQL string and data tuple for use in a row insertion to the stocks table"""
        cusip = row[3]
        symbol = row[0].replace(' ', '.') + suffix
        name = row[2]
        SQL = "INSERT INTO stocks (cusip, symbol, name, country, updated) VALUES (%s, %s, %s, %s, %s);"
        data = (cusip, symbol, name, country, updated,)
        return SQL, data

    @staticmethod
    def _update_stocks(row, updated):
        """Returns SQL string and data tuple for use in row update for the stocks updates"""
        cusip = row[3]
        SQL = "UPDATE stocks SET updated = %s WHERE cusip = %s;"
        data = (updated, cusip,)
        return SQL, data

    @staticmethod
    def _insert_borrow(row, datetime):
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

    #########

    @timer
    def name_search(self, name):
        """Method to return summary report of companies matching a search by name query"""
        name = ''.join(c for c in name if (c.isalnum() or c == ' '))

        db, cursor = self._connect()
        SQL = "SELECT symbol, similarity(name, %s) AS sml FROM stocks WHERE name %% %s ORDER BY sml DESC, name limit 10;"
        data = (name, name, )
        cursor.execute(SQL, data)
        results = cursor.fetchall()

        return self.summary_report([row[0] for row in results])

    @timer
    def insert_watchlist(self, userid, symbols):
        """Takes a userid and list of symbols, adds them to the watchlist database.
        Returns a list of symbols added, and a list of symbols failed to be added"""

        # Sanitize symbols
        safe_symbols = [symbol.upper() for symbol in symbols if Borrow._check_symbol(symbol)]

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

            if cusips:

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
        safe_symbols = [symbol.upper() for symbol in symbols if Borrow._check_symbol(symbol)]

        # Make sure symbols to be removed are on the user's wishlist
        current_watchlist = self.get_watchlist(userid)
        symbols_to_remove = [symbol for symbol in safe_symbols if symbol in current_watchlist]

        if symbols_to_remove:
            db, cursor = self._connect()
            SQL = "SELECT cusip FROM stocks WHERE symbol = ANY(%s);"

            cursor.execute(SQL, (symbols_to_remove,))
            cusips = cursor.fetchall()

            # Build a list of symbols that were actually removed from the watchlist (valid ones essentially)
            SQL = "SELECT symbol FROM stocks WHERE cusip = ANY(%s)"
            cursor.execute(SQL, [cusips])

            symbols_removed = [row[0] for row in cursor.fetchall()]

            # Remove the cusips and userid from the watchlist
            for cusip in cusips:
                SQL = "DELETE FROM watchlist WHERE userid = %s AND cusip = %s;"
                data = (userid, cusip[0],)
                cursor.execute(SQL, data)

            db.commit()
            db.close()

        else:
            return None

        # Return a list of symbols removed
        return symbols_removed

    @timer
    def get_watchlist(self, userid):
        """Get a list of stocks that a user has on his/her watchlist"""

        db, cursor = self._connect()
        SQL = "SELECT symbol FROM stocks WHERE cusip = ANY(SELECT cusip FROM watchlist WHERE userid = %s);"
        data = (userid,)
        cursor.execute(SQL, data)
        results = cursor.fetchall()
        db.close()

        # list comprehension to extract the watchlist
        return [result[0] for result in results]



    @timer
    def filter_db(self, min_available=0, max_available=10000000,
                  min_fee=0, max_fee=100, country='usa', order_by='symbol'):
        """General filter_db function."""

        country = country.lower()

        if order_by not in ['symbol', 'fee', 'available']:
            raise ValueError('Attempted to sort by an invalid field. Only symbol, fee, available allowed')

        if order_by == 'symbol':
            direction = 'ASC'
        else:
            direction = 'DESC'

        db, cursor = self._connect()

        # This query searches across the borrow database using only the most recent entry for each security
        SQL = """SELECT symbol, rebate, fee, available, datetime, name, country
                FROM stocks JOIN borrow ON
                (stocks.cusip = borrow.cusip AND stocks.updated = borrow.datetime)
                WHERE available > %s AND available < %s
                AND fee > %s AND fee < %s
                AND country = %s
                ORDER by %s %s
                LIMIT 100;"""
        data = (min_available, max_available, min_fee, max_fee, country, AsIs(order_by), AsIs(direction))
        cursor.execute(SQL, data)
        results = cursor.fetchall()
        db.close()

        summary = [Stock._make(row) for row in results]

        print("Running Filter")
        print(country)
        print(min_available, ' ', max_available)
        print(min_fee, ' ', max_fee)
        print(order_by)

        return summary

    @timer
    def summary_report(self, symbols):
        """Return a sorted by symbol list of dictionaries including symbols and latest rebate,
        fee, availability, and date/time of last update"""

        safe_symbols = []
        for symbol in symbols:
            if Borrow._check_symbol(symbol) and symbol.upper() in self.all_symbols:
                safe_symbols.append(symbol.upper())

        if safe_symbols:
            # Select the most recent row for each symbol being searched for
            db, cursor = self._connect()
            SQL = """SELECT DISTINCT symbol, rebate, fee, available, datetime, name, country
                    FROM stocks JOIN borrow ON
                    (stocks.cusip = borrow.cusip AND stocks.updated = borrow.datetime)
                    WHERE symbol = ANY(%s)
                    ORDER BY symbol;"""
            data = (safe_symbols,)
            cursor.execute(SQL, data)

            results = cursor.fetchall()
            db.close()

            # Make a Stock for each row in the results and add to list
            return [Stock._make(row) for row in results]

        else:
            return None

    @timer
    def historical_report(self, symbol, real_time=False):
        """Return historical report of rebate, fee, availability for a given symbol  along with the Company name
        The default interval is daily (9:30AM for the opening of the market) - if real-time flag is set to True
        the last 100 entries will be returned - about 3 days of data."""
        if Borrow._check_symbol(symbol):
            safe_symbol = symbol.upper()
        else:
            return None

        db, cursor = self._connect()
        data = (safe_symbol,)



        if real_time:
            SQL = """SELECT rebate, fee, available, datetime FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip)
                    WHERE symbol = %s AND borrow.datetime > now() - interval '7days'
                    ORDER BY datetime DESC;"""

        else:
            SQL = """SELECT rebate, fee, available, cast(datetime as date) as date
                    FROM stocks JOIN Borrow ON (stocks.cusip = Borrow.cusip)
                    WHERE symbol = %s
                    AND cast(datetime as time) between '9:30' and '9:40'
                    ORDER BY datetime DESC
                    LIMIT 90;"""

        cursor.execute(SQL, data)
        results = [{'rebate': float(row[0])/100, 'fee': float(row[1])/100, 'available': float(row[2]), 'time': row[3].isoformat()} for
                   row in
                   cursor.fetchall()]

        # If the search didn't find anything return None
        if results:
            return results
        else:
            return None

    @timer
    def search(self, symbol, userid=None):
        """Method to record searches of the database"""

        db, cursor = self._connect()

        data = (symbol, userid, datetime.now())
        SQL = """INSERT INTO search(symbol, userid, datetime) VALUES(%s, %s, %s);"""
        cursor.execute(SQL, data)
        db.commit()
        db.close()


    def get_company_name(self, symbol):
        """Returns the name of a Company given a symbol. Returns None if no symbol exists"""
        if Borrow._check_symbol(symbol):
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
            print('Symbol not found')
            db.close()
            return None
        db.close()
        return name

    @timer
    def refresh_latest_all_symbols(self):
        """Set the instance variable list of every symbol in the latest update from IB"""
        db, cursor = self._connect()
        SQL = """SELECT distinct symbol FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip)
                WHERE datetime = (SELECT max(datetime) FROM borrow);"""
        cursor.execute(SQL)

        self.latest_symbols = [row[0] for row in cursor.fetchall()]
        db.close()

    @timer
    def refresh_all_symbols(self):
        """Set the list of all symbols in the database"""
        db, cursor = self._connect()
        SQL = """SELECT DISTINCT symbol FROM stocks;"""
        cursor.execute(SQL)

        self.all_symbols = [row[0] for row in cursor.fetchall()]
        db.close()


    @timer
    def clean_dbase(self):
        """Remove entries _not_ bw 0925 and 0935 older than 1 week. Maintains historical record
        while getting rid of stale intraday data"""
        db, cursor = self._connect()
        SQL = """DELETE FROM Borrow
              WHERE cast(datetime as time) NOT BETWEEN '9:25' and '9:35'
              AND datetime < now() - interval '7days';"""

        cursor.execute(SQL)
        db.commit()

        # Update the most recent updated column in the stocks table in case the most recent entry was deleted



       # TODO: THINK ABOUT THIS MORE
        # for symbol in self.all_symbols:
        #     SQL = """SELECT max(datetime) FROM borrow JOIN stocks ON (stocks.cusip = borrow.cusip) WHERE symbol = %s;"""
        #     data = (symbol,)
        #     cursor.execute(SQL, data)
        #
        #     last_updated = cursor.fetchone()[0]
        #     SQL = "UPDATE stocks SET updated = %s WHERE symbol = %s;"
        #     data = (last_updated, symbol)
        #     cursor.execute(SQL, data)
        #     db.commit()

        db.close()

        return None

    @timer
    def update_trending(self):
        """
        Updates lists of 'trending' stocks - ie; those stocks with large changes in fees or availability from average
        """
        db, cursor = self._connect()

        min_fee = 20
        min_available = 10000
        data = (min_fee, min_available,)

        SQL = """SELECT stocks.symbol FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip AND stocks.updated = borrow.datetime)
                JOIN
                    (SELECT symbol, avg(fee) as avg_fee
                    FROM stocks JOIN borrow ON
                        (stocks.cusip = borrow.cusip)
                    WHERE symbol in
                        (SELECT symbol FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip AND stocks.updated = borrow.datetime)
                            WHERE fee > %s AND available > %s)
                    AND borrow.datetime > now() - interval '7days'
                    GROUP BY symbol) as avg_table
                ON avg_table.symbol = stocks.symbol
                ORDER BY fee/avg_table.avg_fee DESC
                LIMIT 20;"""

        cursor.execute(SQL, data)
        rows = cursor.fetchall()
        self.trending_fee = [row[0] for row in rows]

        SQL = """SELECT stocks.symbol FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip AND stocks.updated = borrow.datetime)
                JOIN
                    (SELECT symbol, avg(available) as avg_available
                    FROM stocks JOIN borrow ON
                        (stocks.cusip = borrow.cusip)
                    WHERE symbol in
                        (SELECT symbol FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip AND stocks.updated = borrow.datetime)
                            WHERE fee > %s AND available > %s)
                    AND borrow.datetime > now() - interval '7days'
                    GROUP BY symbol) as avg_table
                ON avg_table.symbol = stocks.symbol
                ORDER BY available/avg_table.avg_available
                LIMIT 20;"""

        cursor.execute(SQL, data)
        rows = cursor.fetchall()
        self.trending_available = [row[0] for row in rows]


    @staticmethod
    def _check_symbol(text):
        """Ensure a symbol is safe for the database
        :rtype : Boolean
        """
        if re.match("^[\sa-zA-Z0-9\.]{1,15}$", text) is not None:
            return True
        else:
            return False
