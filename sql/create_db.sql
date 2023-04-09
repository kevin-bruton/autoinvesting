CREATE DATABASE AutoInvesting;

CREATE TABLE Users (
    username varchar(55) NOT NULL PRIMARY KEY,
    passwd varchar(55),
    email varchar(55),
    firstName varchar(55),
    lastName varchar(55),
    city varchar(55),
    country varchar(55),
    accountType varchar(55) DEFAULT 'investor'
);

CREATE TABLE Accounts (
  accountId VARCHAR(55) NOT NULL,
  accountNumber VARCHAR(55) NOT NULL,
  accountType ENUM('demo', 'real', 'strategy_demo', 'strategy_backtest'),
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

CREATE TABLE Strategies (
    magic BIGINT NOT NULL,
    strategyName VARCHAR(255) NOT NULL,
    symbols VARCHAR(255) NOT NULL,
    timeframes VARCHAR(55) NOT NULL,
    description TEXT,
    workflow VARCHAR(255),
    PRIMARY KEY (magic)
);

CREATE TABLE Orders (
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

CREATE TABLE Subscriptions (
  magicAccountId VARCHAR(255) NOT NULL,
  accountId VARCHAR(55) NOT NULL,
  magic BIGINT NOT NULL,
  PRIMARY KEY (magicAccountId),
  FOREIGN KEY (accountId) REFERENCES Accounts(accountId),
  FOREIGN KEY (magic) REFERENCES Strategies(magic)
);

CREATE TABLE Trades (
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

CREATE TABLE Updates (
    updateTime DATETIME NOT NULL PRIMARY KEY,
    result TEXT
);
