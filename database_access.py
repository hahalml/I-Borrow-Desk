import csv
import psycopg2
from timed_function import timer
from ftplib import FTP
import time

def ftp_update():
    '''Connect to the IB ftp server and download the latest usa.txt file
    Write to disk a filename based on the current GMT time and use that file
    to update the borrow database'''
    time_stamp = time.strftime('%Y-%m-%d %H %M %S', time.gmtime())
    filename = 'usa' + time_stamp + '.txt'

    connection = FTP('ftp3.interactivebrokers.com', 'shortstock')
    connection.retrbinary('RETR usa.txt', open(filename, 'wb').write)
    update_borrow(filename)


def connect(database_name="stock_loan"):
    """Connect to the PostgreSQL database.  Returns a database connection. Default database is 'stock_loan' """
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("Could not find the %s database." % database_name)

@timer
def initialize_dbase(filename = 'usa.txt'):
    rows = []
    with open(filename, 'rb') as csvfile:
        stockreader = csv.reader(csvfile, delimiter='|')
        for row in stockreader:
            rows.append(row)

    rows = rows[2:]

    db, cursor = connect()
    query = ''

    for row in rows:
        try:
            SQL, data = insert_stocks(row)
            cursor.execute(SQL, data)
            db.commit()
        except IndexError:
            print 'Index error caught'

    db.close()


@timer
def update_borrow(filename = 'usa.txt'):
    rows = []
    with open(filename, 'rb') as csvfile:
        stockreader = csv.reader(csvfile, delimiter='|')
        for row in stockreader:
            rows.append(row)

    date = rows[0][1].replace('.','-')
    time = rows[0][2]

    print date, time

    # Cut off the first two rows that don't contain stock data
    rows = rows[2:]

    db, cursor = connect()
    query = ''

    for row in rows:
        try:
            SQL, data = insert_borrow(row, date, time)
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
            SQL, data = insert_stocks(row)
            cursor.execute(SQL, data)
            db.commit()

            SQL, data = insert_borrow(row, date, time)
            cursor.execute(SQL, data)
            db.commit()

        except psycopg2.InternalError:
            print 'Internal Error caught'

    db.close()

def insert_stocks(row):
    '''Returns SQL string and data tuple for use in a row insertion to the stocks table '''
    cusip = row[3]
    symbol = row[0]
    name = row[2]
    SQL = "INSERT INTO stocks (cusip, symbol, name) VALUES (%s, %s, %s);"
    data = (cusip, symbol, name,)
    return SQL, data

def insert_borrow(row, date, time):
    '''Returns SQL string and data tuple for use in a row insertion to the borrow table'''
    cusip = row[3]
    # Replace NA rebates and fees with nonsensical dummy values
    rebate = row[5].replace('NA','99')
    fee = row[6].replace('NA','-99')

    # Ignore '>' symbol
    available = row[7].replace('>', '')

    SQL = "INSERT INTO borrow (date, time, cusip, rebate, fee, available) VALUES (%s, %s, %s, %s, %s, %s);"
    data = (date, time, cusip, rebate, fee, available,)
    return SQL, data







@timer
def tight_borrow(available = 5000):
    db, cursor = connect()
    query = "SELECT symbol, available FROM stocks JOIN borrow ON (stocks.cusip = borrow.cusip) WHERE available < %s;"
    data = (available,)
    cursor.execute(query, data)
    results = cursor.fetchall()
    return results


#initialize_dbase()
#update_borrow()

#tight_borrow()