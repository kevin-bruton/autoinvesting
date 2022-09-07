CREATE TABLE Kpis (
  kpiId INTEGER NOT NULL AUTO_INCREMENT,
  runId INTEGER NOT NULL,
  annualPctRet DECIMAL(10,2),
  maxDD DECIMAL(10,2),
  maxPctDD DECIMAL(10,2),
  annPctRetVsDdPct DECIMAL(10,3),
  winPct DECIMAL(10,2),
  profitFactor DECIMAL(10,2),
  numTrades INTEGER,
  PRIMARY KEY (kpiId),
  FOREIGN KEY (runId) REFERENCES StrategyRun(runId)
);
