CREATE TABLE Positions (
  orderId VARCHAR(55) NOT NULL,
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
