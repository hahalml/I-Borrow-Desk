import Quandl
from Quandl.Quandl import DatasetNotFound

from borrow import Borrow

with open('quandl.txt') as f:
    auth_token = f.read()

shares_out = []


stock_loan=Borrow()
symbols = stock_loan.filter(order_by='fee')

for symbol in symbols[:100]:
    request_string = "SEC/{}MARKETCAPITALIZATION_Q".format(symbol['symbol'])
    print(request_string)

    try:
        data = Quandl.get(request_string, authtoken=auth_token)
        shares_out.append({symbol['symbol'] : int(data[-1:]['Value'].iloc[0])})
    except DatasetNotFound:
        print('Dur')


print(shares_out)

