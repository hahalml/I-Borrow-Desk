-- Table definitions for stock loan application

CREATE DATABASE stock_loan;

\c stock_loan

CREATE TABLE stocks (cusip INT PRIMARY KEY, symbol TEXT, name TEXT, country TEXT, latest_fee DECIMAL,
latest_available DECIMAL, updated TIMESTAMP);

CREATE TABLE borrow (id SERIAL PRIMARY KEY, datetime TIMESTAMP,
	cusip INT REFERENCES stocks(cusip) ON DELETE CASCADE, fee DECIMAL, available INT);

CREATE TABLE watchlist (userid INT, cusip INT REFERENCES stocks(cusip));

CREATE TABLE search (id SERIAL PRIMARY KEY, symbol TEXT, userid INT, datetime TIMESTAMP);