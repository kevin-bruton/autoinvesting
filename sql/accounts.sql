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
  PRIMARY KEY (accountId),
  FOREIGN KEY (username) REFERENCES Users(username)
);
