import sys
import sqlite3
from os import getenv

db_path = getenv('DB_DIR') + '/autoinvesting.db'
datetime_fmt = '%Y-%m-%d %H:%M:%S'
values_placeholder = lambda fields: ','.join(['?'] * len(fields.split(',')))

def mutate_one(sql, values: tuple):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path)
  rows_affected = 0
  try:
    c = conn.cursor()
    c.execute(sql, values)
    conn.commit()
    rows_affected = c.rowcount
  finally:
    conn.close()
  return rows_affected

def mutate_many(sql, values: list[tuple]):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path)
  rows_affected = 0
  try:
    c = conn.cursor()
    c.executemany(sql, values)
    conn.commit()
    rows_affected = c.rowcount
  finally:
    conn.close()
  return rows_affected

def query_one(sql, values=()):
  conn = sqlite3.connect(db_path)
  try:
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(sql, values)
    result = c.fetchone()
    return result
  finally:
    conn.close()


def query_many(sql, values: list[tuple] = None):
  conn = sqlite3.connect(db_path)
  try:
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute(sql, values) if values else c.execute(sql)
    result = c.fetchall()
    return result
  finally:
    conn.close()

def init_db():
  try:
    conn = sqlite3.connect(db_path)
  except sqlite3.Error as e:
    print('ERROR: Could not create or connect to the database.\n')
    print(f'Make sure the following directory exists: {get_config_value("database_directory")}')
    print('as that is the directory you have specified in your config file.')
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
        accountNumber VARCHAR(55) NOT NULL,
        accountType VARCHAR(55) CHECK(accountType IN ('demo', 'real', 'strategy_demo', 'strategy_backtest')),
        username VARCHAR(55) NOT NULL,
        subscriptionKey VARCHAR(255),
        startDate DATE,
        endDate DATE,
        deposit FLOAT(9),
        annualPctRet DECIMAL(10,2),
        maxDD DECIMAL(10,2),
        maxPctDD DECIMAL(10,2),
        annPctRetVsDdPct DECIMAL(10,3),
        winPct DECIMAL(10,2),
        profitFactor DECIMAL(10,2),
        numTrades INTEGER,
        lastHeartbeat DATETIME,
        lastConnectionUpdate DATETIME,
        isConnected TINYINT(1) DEFAULT 0,
        PRIMARY KEY (accountId),
        FOREIGN KEY (username) REFERENCES Users(username)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Strategies (
          magic BIGINT NOT NULL,
          strategyName VARCHAR(255) NOT NULL,
          symbols VARCHAR(255) NOT NULL,
          timeframes VARCHAR(55) NOT NULL,
          description TEXT,
          workflow VARCHAR(255),
          decommissioned DATETIME,
          PRIMARY KEY (magic)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Orders (
        orderId VARCHAR(55) NOT NULL,
        status VARCHAR(55),
        masterOrderId VARCHAR(55),
        accountId VARCHAR(55) NOT NULL,
        magic BIGINT,
        symbol VARCHAR(55),
        orderType VARCHAR(55),
        openTime DATETIME,
        openPrice FLOAT,
        size DECIMAL(4,2),
        comment VARCHAR(255),
        sl FLOAT,
        tp FLOAT,
        PRIMARY KEY (orderId),
        FOREIGN KEY (accountId) REFERENCES Accounts(accountId),
        FOREIGN KEY (magic) REFERENCES Strategies(magic)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Subscriptions (
        magicAccountId VARCHAR(255) NOT NULL,
        accountId VARCHAR(55) NOT NULL,
        magic BIGINT NOT NULL,
        PRIMARY KEY (magicAccountId),
        FOREIGN KEY (accountId) REFERENCES Accounts(accountId),
        FOREIGN KEY (magic) REFERENCES Strategies(magic)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Trades (
        orderId VARCHAR(55) NOT NULL,
        accountId VARCHAR(55) NOT NULL,
        masterOrderId VARCHAR(55),
        magic BIGINT NOT NULL,
        symbol VARCHAR(55),
        orderType VARCHAR(55),
        openTime DATETIME,
        closeTime DATETIME,
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
        FOREIGN KEY (magic) REFERENCES Strategies(magic)
      );
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS Updates (
          updateTime DATETIME NOT NULL PRIMARY KEY,
          result TEXT
      );
      ''')
    conn.commit()
  finally:
    conn.close()
