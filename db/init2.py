import sys
import sqlite3
from os import getenv

def init_db():
  db_path = getenv('DB_FILE')
  try:
    conn = sqlite3.connect(db_path)
  except sqlite3.Error as e:
    print('ERROR: Could not create or connect to the database.\n')
    print(f'Make sure the directory of this file exists: {getenv("DB_FILE")}')
    print('Make sure you have write permissions to that directory.')
    input('\nPress any key to exit...')
    sys.exit(1)
  try:
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS Users (
          username varchar(55) NOT NULL PRIMARY KEY,
          passwd varchar(55),
          email varchar(55),
          firstName varchar(55),
          lastName varchar(55),
          city varchar(55),
          country varchar(55),
          accountType varchar(55) DEFAULT 'investor'
          );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Accounts (
        accountId VARCHAR(55) NOT NULL,
        accountType VARCHAR(55) CHECK(accountType IN ('paper', 'live')),
        broker VARCHAR(55),
        platform VARCHAR(55) CHECK(platform in ('MetaTrader', 'Multicharts')),
        username VARCHAR(55) NOT NULL,
        balance FLOAT(9),
        lastConnectionUpdate TIMESTAMP,
        isConnected TINYINT(1) DEFAULT 0,
        PRIMARY KEY (accountId),
        FOREIGN KEY (username) REFERENCES Users(username)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Strategies (
          strategyId VARCHAR(255) NOT NULL,
          friendlyName VARCHAR(255),
          magic BIGINT,
          type VARCHAR(55),
          description TEXT,
          workflow VARCHAR(255),
          decommissioned TIMESTAMP,
          PRIMARY KEY (strategyId)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS StrategyRuns (
          strategyRunId VARCHAR(255) NOT NULL,
          strategyId VARCHAR(255) NOT NULL,
          accountId VARCHAR(255),
          type VARCHAR(55) CHECK(type in ('backtest', 'paper', 'live' )),
          platform VARCHAR(55) CHECK(platform in ('MetaTrader', 'Multicharts')),
          symbol VARCHAR(255) NOT NULL,
          timeframe VARCHAR(55) NOT NULL,
          startDate TIMESTAMP,
          endDate TIMESTAMP
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Orders (
        orderId VARCHAR(55) NOT NULL,
        status VARCHAR(55),
        accountId VARCHAR(55) NOT NULL,
        strategyId VARCHAR(255),
        symbol VARCHAR(55),
        orderType VARCHAR(55),
        openTime TIMESTAMP,
        openPrice FLOAT,
        size DECIMAL(4,2),
        comment VARCHAR(255),
        sl FLOAT,
        tp FLOAT,
        PRIMARY KEY (orderId),
        FOREIGN KEY (accountId) REFERENCES Accounts(accountId),
        FOREIGN KEY (strategyId) REFERENCES Strategies(strategyId)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Trades (
        orderId VARCHAR(55) NOT NULL,
        accountId VARCHAR(55) NOT NULL,
        strategyId VARCHAR(255),
        symbol VARCHAR(55),
        orderType VARCHAR(55),
        openTime TIMESTAMP,
        closeTime TIMESTAMP,
        openPrice FLOAT,
        closePrice FLOAT,
        size DECIMAL(4,2),
        profit DECIMAL(10,2),
        balance DECIMAL(10,2),
        closeType VARCHAR(55),
        comment VARCHAR(255),
        sl FLOAT,
        tp FLOAT,
        swap DECIMAL(10,2),
        commission DECIMAL(10,2),
        PRIMARY KEY (orderId),
        FOREIGN KEY (accountId) REFERENCES Accounts(accountId),
        FOREIGN KEY (strategyId) REFERENCES Strategies(strategyId)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Updates (
          updateTime TIMESTAMP NOT NULL PRIMARY KEY,
          result TEXT
      );
      ''')
    conn.commit()
  finally:
    conn.close()
