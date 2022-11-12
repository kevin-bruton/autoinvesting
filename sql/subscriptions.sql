CREATE TABLE Subscriptions (
  magicAccountId VARCHAR(255) NOT NULL AUTOINCREMENT,  
  accountId VARCHAR(55) NOT NULL,
  magic INT NOT NULL,
  PRIMARY KEY (magicAccountId),
  FORIEGN KEY (accountId) REFERENCES Accounts(accountId),
  FORIEGN KEY (magic) REFERENCES Strategies(magic)
);
