CREATE TABLE AccountsHistory (
  accountBalanceId VARCHAR(55) NOT NULL,
  accountId VARCHAR(55) NOT NULL,
  balance INT,
  date DATETIME,
  PRIMARY KEY (accountBalanceId),
  FOREIGN KEY (accountId) REFERENCES Accounts(accountId)
);
