import ConfigParser
import os
import time
import re

TICKER_MATCH = re.compile(r"\$([a-zA-Z]{1,4})")

from twython import TwythonStreamer
from twython import Twython

# import the stock loan access instance from routes
from routes import stock_loan

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

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        self.disconnect()
        print "Disconnected"

    def _respond(self, data):

        # Grab the tweet's text and try to extract a symbol from it
        text = data['text'].encode('utf-8')
        match = TICKER_MATCH.search(text)
        if match:

            # Extract the ticker and run a summary report on it
            ticker = match.group(0)[1:]
            summary = stock_loan.summary_report([ticker])

            # Confirm the summary report is not empty
            if summary != []:
                summary = summary[0]

                #extract the relevent information from the summary report and build a status string
                symbol = summary['symbol']
                available = '{:,}'.format(summary['available'])
                fee = '{:.1%}'.format(summary['fee']/100)
                datetime = summary['datetime']
                url = 'http://ec2-52-27-34-15.us-west-2.compute.amazonaws.com/historical_report?symbol=%s&&real_time=True' %symbol

                screen_name = data['user']['screen_name'].encode('utf-8')

                status = '@%s Symbol: %s, Available: %s, Fee: %s, Last Updated: %s ' \
                         %(screen_name, symbol, available, fee, datetime)
                status = status + url

                # Grab the id of the user that tweeted at the bot
                id_str = data['id_str'].encode('utf-8').encode('utf-8')

                # Update status
                self._twitter.update_status(status=status, in_reply_to_status_id=id_str)

                print 'Match found %s' %ticker
                print 'Responded with %s' %status

            else:
                print 'Invalid symbol matched'
        else:
            print 'No match found'


def run_twitter_stream():
    stream = BorrowStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    stream.statuses.filter(track='@IBorrowDesk')