CREATE TABLE StrategyRuns (
  runId VARCHAR(55) NOT NULL,
  magic BIGINT NOT NULL,
  runType ENUM('backtest', 'demo', 'real'),
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
  PRIMARY KEY (runId),
  FOREIGN KEY (magic) REFERENCES Strategies(magic)
);
