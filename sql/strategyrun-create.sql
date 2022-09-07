CREATE TABLE StrategyRun (
  runId INTEGER NOT NULL AUTO_INCREMENT,
  magic BIGINT NOT NULL,
  runType ENUM('backtest', 'demo', 'real'),
  startDate DATE,
  endDate DATE,
  deposit FLOAT(9),
  PRIMARY KEY (runId),
  FOREIGN KEY (magic) REFERENCES Strategies(magic)
);
