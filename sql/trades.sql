CREATE TABLE Trades (
    tradeId INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    strategyName VARCHAR(55),
    symbol VARCHAR(55),
    environment ENUM('backtest', 'demo', 'live'),
    platform ENUM('SQX', 'MT4', 'MT5', 'Tradestation'),
    direction VARCHAR(55),
    size DOUBLE,
    profit DOUBLE,
    balance DOUBLE,
    timeInTrade VARCHAR(55),
    closeType VARCHAR(55),
    openTime DATETIME,
    closeTime DATETIME,
    openPrice DOUBLE,
    closePrice DOUBLE
);

INSERT INTO Trades (strategyName, magic, symbol, direction, size, profit, balance, timeInTrade, closeType, openTime, closeTime, openPrice, closePrice)
VALUES ('superBot', 202206101, 'WS30', 'Buy', 0.04, 44.20, 1044.20, '1d 16h 0m', 'Exit After X Bars', '2013-11-06 05:00:00', '2013-11-07 21:00:00', 15651.9, 15661.9);
