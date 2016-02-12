import React from 'react';
import { Link } from 'react-router';

export default () => {
  return (
    <div>
      <h4>About</h4>
      <p>IBorrow Desk is a tool for monitoring borrow rates and availability using
        Interactive Broker's freely available data.</p>
      <p>I worked in finance for the past five years, with my last year or so doing a
        decent amount of short selling. One of the resources I used quite a lot was
        Interactive Broker's <a href="https://ibkb.interactivebrokers.com/article/2024">
          Stock Loan Availability Database</a> especially for hard to borrow stocks.</p>
      <p>But it was a pain to keep updated and an overall a pain to use. So,
        after taking Udacity's <a href="https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004">
          Full Stack Nanodegree</a> I figured this database would be a fun place to start
        building a working (maybe even useful) web app.</p>
      <p>Built in Python, I used the Flask framework and SQLAlchemy for the user database and PostgreSQL
        for the borrow database. Memcached caches historical reports for those pesky Twitter bots.</p>
      <p> The front-end was rebuilt entirely in the beginning of 2016 using
        <a href="https://facebook.github.io/react/">React</a> and <a href="http://redux.js.org/">Redux</a>.</p>
      <p>Speaking of Twitter bots, <a href="https://twitter.com/IBorrowDesk">@IBorrowDesk </a>
         has access to this database. Tweet a ticker symbol at it and it will tweet back its fee and availability!</p>
      <p>You can reach me at <mail to="cameron.mochrie@gmail.com">cameron.mochrie@gmail.com</mail>.
        The source for I Borrow Desk is available at <a href="https://github.com/cjmochrie/I-Borrow-Desk">
          GitHub</a>.</p>

      <h4>FAQ</h4>
      <p><strong>Who are you?</strong> I worked in finance in Toronto until earlier this year. I am attempting to
        switch careers into software development and this web-app is my first 'product'. Please be patient as I've only
        been doing this for a couple of months (since May '15)!</p>

        <p><strong>What exactly does this thing do?</strong> Downloads a series of csv files from the Interactive Broker's
        FTP site, chucks everything into a postgreSQL database and displays it on your screen.</p>

        <p><strong>What are the benefits of registering?</strong> Registered users can create a watchlist
        of symbols (similar format to the front page) to track stocks they are interested in. Every weekday morning,
        (if you like) you will receive an email summarizing the current rates and availability for the symbols
            on your watch list.
        In the future I hope to add some alerts for big changes in availability/rates, or manually set thresholds.</p>

        <p><strong>What is the ticker structure?</strong> I'm currently tracking Interactive Broker's worldwide database
        which includes: Australia, Austria, Belgium, UK, Canada, Netherlands, France, Germany, Hong Kong, India, Italy,
            Japan, Mexico, Spain, Sweden, Switzerland, and the USA. US tickers do not have a suffix, while all other
        countries do (in the form: <Link to='report/ABX.CA'>ABX.CA</Link>
            - Barrick Gold) I have tried to match country codes based on
            <a href="http://risk101.com/reference/Techdoc-Bloomberg_country_codes.pdf">Bloomberg's</a> methodology. Let me know
        if you spot any errors.</p>

        <p><strong>How often is the database updated?</strong> Every 15 minutes around trading hours on weekdays (so almost
            24 hours a day given the global scope within a minute of IB refreshing on their end.</p>

        <p><strong>How far back does the data go?</strong> Historical data (one row/day) will be retained indefinitely
            and 'real-time' (every 15 minutes) data is retained for one week.</p>
    </div>
  )
}