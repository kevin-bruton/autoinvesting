CREATE TABLE Trades (
    tradeId INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    strategyName VARCHAR(55),
    symbol VARCHAR(55),
    environment ENUM('backtest', 'demo', 'live'),
    platform ENUM('SQX', 'MT4', 'MT5', 'Tradestation'),
    direction VARCHAR(55),
    size DOUBLE,
    profit DOUBLE,
    openTime DATETIME,
    closeTime DATETIME,
    openPrice DOUBLE,
    closePrice DOUBLE,
    closeType VARCHAR(55),
    comment VARCHAR(255)
);
