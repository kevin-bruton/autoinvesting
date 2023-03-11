CREATE TABLE Subscriptions (
  magicAccountId VARCHAR(255) NOT NULL,
  accountId VARCHAR(55) NOT NULL,
  magic BIGINT NOT NULL,
  PRIMARY KEY (magicAccountId),
  FOREIGN KEY (accountId) REFERENCES Accounts(accountId),
  FOREIGN KEY (magic) REFERENCES Strategies(magic)
);
