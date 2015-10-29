import configparser
import os
import re
from twython import TwythonStreamer
from twython import Twython
from borrow import Borrow

dirname, file_name = os.path.split(os.path.abspath(__file__))

# Grab Twitter  config
parser = configparser.ConfigParser()
parser.read(dirname + '/twitter_settings.cfg')
APP_KEY = parser.get('twitter', 'APP_KEY')
APP_SECRET = parser.get('twitter', 'APP_SECRET')
OAUTH_TOKEN = parser.get('twitter', 'OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = parser.get('twitter', 'OAUTH_TOKEN_SECRET')

TICKER_MATCH = r"\$([a-zA-Z0-9\.]{1,8})"

class BorrowStreamer(TwythonStreamer):
    """Twitter Streamer class for responding to tweets at the bot"""
    def __init__(self, *a, **kwargs):
        # Create a Twitter Rest API instance for responding to tweets
        #self._twitter = Twython(*a)

        # Create a Borrow instance
        self._stock_loan = Borrow(database_name='stock_loan', create_new=False)

        TwythonStreamer.__init__(self, *a, **kwargs)

    def on_success(self, data):
        """If the streamer receives a tweet that matches its filter"""
        if 'text' in data:
            # Check that it wasn't one of the bot's own tweets
            if data['user']['screen_name'] != 'IBorrowDesk':
                #Print out the tweet's text, author screename and id
                # and call the respond function
                print(data['text'])
                print(data['user']['screen_name'])
                print(data['id_str'])
                self._respond(data)


    def on_error(self, status_code, data):
        print(status_code)
        print(data)
        print("There was an error")

    def _respond(self, data):

        #
        twitter_rest = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

        # Grab the tweet's text and try to extract a symbol from it
        text = data['text']
        matches = re.findall(TICKER_MATCH, text)
        print('matches were {} \n'.format(str(matches)))
        if matches:
            summary = self._stock_loan.summary_report(matches)
            print(summary)

            # Confirm the summary report is not empty
            if summary != None:
                for ticker in summary:
                    print(ticker.symbol)

                    #extract the relevant information from the
                    # summary report and build a status string
                    symbol = ticker.symbol
                    name = ticker.name[:20]
                    available = '{:,}'.format(ticker.available)
                    fee = '{:.1%}'.format(ticker.fee/100)
                    datetime = ticker.datetime
                    url = 'http://cameronmochrie.com/IBorrowDesk/historical_report?symbol={}&&real_time=False'.\
                        format(symbol)
                    screen_name = data['user']['screen_name']

                    status = '@{} ${} {}, Available: {}, Fee: {}, Last Updated: {} '.\
                        format(screen_name, symbol, name, available, fee, datetime)
                    status = status + url

                    # Grab the id of the user that tweeted at the bot
                    id_str = data['id_str']

                    # Update status
                    twitter_rest.update_status(status=status, in_reply_to_status_id=id_str)

                    print('Match found {} \n'.format(ticker))
                    print('Responded with {} \n'.format(status))

            else:
                print('Invalid symbols matched \n')
        else:
            print('No match found \n')


stream = BorrowStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
stream.statuses.filter(track='@IBorrowDesk')
