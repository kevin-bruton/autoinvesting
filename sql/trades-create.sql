CREATE TABLE Trades (
  orderId INTEGER NOT NULL AUTO_INCREMENT,
  runId INTEGER NOT NULL,
  symbol VARCHAR(55),
  orderType VARCHAR(55),
  openTime DATETIME,
  closeTime DATETIME,
  openPrice FLOAT,
  closePrice FLOAT,
  size DECIMAL(4,2),
  profit DECIMAL(10,2),
  closeType VARCHAR(55),
  comment VARCHAR(255),
  PRIMARY KEY (orderId),
  FOREIGN KEY (runId) REFERENCES StrategyRun(runId)
);
