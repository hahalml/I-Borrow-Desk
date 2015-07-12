-- Table definitions for stock loan application

CREATE DATABASE stock_loan;

\c stock_loan

CREATE TABLE stocks (cusip INT PRIMARY KEY, symbol TEXT, name TEXT, country TEXT);

CREATE TABLE borrow (id SERIAL PRIMARY KEY, datetime TIMESTAMP,
	cusip INT REFERENCES stocks(cusip) ON DELETE CASCADE, rebate DECIMAL, fee DECIMAL, available INT);

CREATE TABLE watchlist (userid INT, cusip INT REFERENCES stocks(cusip));

