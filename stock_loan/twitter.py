import ConfigParser
import os
import re

TICKER_MATCH = r"\$([a-zA-Z0-9\.]{1,8})"

from twython import TwythonStreamer
from twython import Twython

# import the stock loan access instance from routes
from borrow import Borrow

dirname, file_name = os.path.split(os.path.abspath(__file__))

# Grab Twitter  config
parser = ConfigParser.ConfigParser()
parser.read(dirname + '/twitter_settings.cfg')
APP_KEY = parser.get('twitter', 'APP_KEY')
APP_SECRET = parser.get('twitter', 'APP_SECRET')
OAUTH_TOKEN = parser.get('twitter', 'OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = parser.get('twitter', 'OAUTH_TOKEN_SECRET')

class BorrowStreamer(TwythonStreamer):
    """Twitter Streamer class for responding to tweets at the bot"""
    def __init__(self, *a, **kw):

        # Create a Twitter Rest API instance for responding to tweets
        self._twitter = Twython(*a)

        # Will live inside the actual Streamer object
        TwythonStreamer.__init__(self, *a, **kw)
        print 'in borrow streamer'

        # Create a Borrow instance
        self._stock_loan = Borrow(database_name='stock_loan', create_new=False)

    def on_success(self, data):
        """If the streamer receives a tweet that matches its filter"""
        if 'text' in data:
            # Check that it wasn't one of the bot's own tweets
            if data['user']['screen_name'] != 'IBorrowDesk':
                #Print out the tweet's text, author screename and id and call the respond function
                print data['text'].encode('utf-8')
                print data['user']['screen_name'].encode('utf-8')
                print data['id_str'].encode('utf-8')
                self._respond(data)


    def on_error(self, status_code, data):
        print status_code
        print data

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        #self.disconnect()
        print "There was an error"

    def _respond(self, data):

        # Grab the tweet's text and try to extract a symbol from it
        text = data['text'].encode('utf-8')
        matches = re.findall(TICKER_MATCH, text)
        print 'matches were ' + str(matches)
        if matches:

            summary = self._stock_loan.summary_report(matches)
            print summary
            # Confirm the summary report is not empty
            if summary != None:

                for ticker in summary:
                    print 'looping through symbols'
                    #Grab the summary report (it is the first element in the list)
                    print ticker['symbol']
                    #extract the relevant information from the summary report and build a status string
                    symbol = ticker['symbol']
                    name = ticker['name'][:20]
                    available = '{:,}'.format(ticker['available'])
                    fee = '{:.1%}'.format(ticker['fee']/100)
                    datetime = ticker['datetime']
                    url = 'http://cameronmochrie.com/IBorrowDesk/historical_report?symbol=%s&&real_time=True' %symbol

                    screen_name = data['user']['screen_name'].encode('utf-8')

                    status = '@%s $%s %s, Available: %s, Fee: %s, Last Updated: %s ' \
                             %(screen_name, symbol, name, available, fee, datetime)
                    status = status + url

                    # Grab the id of the user that tweeted at the bot
                    id_str = data['id_str'].encode('utf-8').encode('utf-8')

                    # Update status
                    self._twitter.update_status(status=status, in_reply_to_status_id=id_str)

                    print 'Match found %s' %ticker
                    print 'Responded with %s' %status

            else:
                print 'Invalid symbols matched'
        else:
            print 'No match found'


def run_twitter_stream():
    print 'in run twitter stream'

    stream = BorrowStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    stream.statuses.filter(track='@IBorrowDesk')