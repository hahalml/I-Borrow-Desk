-- Table definitions for stock loan application

CREATE DATABASE stock_loan;

\c stock_loan

CREATE TABLE stocks (cusip INT PRIMARY KEY, symbol TEXT, name TEXT);
CREATE TABLE borrow (id SERIAL PRIMARY KEY, date DATE, time TIME,
	cusip INT REFERENCES stocks(cusip), rebate DECIMAL, fee DECIMAL, available INT);