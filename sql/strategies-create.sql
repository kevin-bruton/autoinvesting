CREATE TABLE Strategies (
    strategyName VARCHAR(255) NOT NULL PRIMARY KEY,
    magic BIGINT,
    symbols VARCHAR(255),
    timeframes VARCHAR(55),
    btStart DATE,
    btEnd DATE,
    btDeposit FLOAT(9,2),
    btTrades LONGTEXT,
    btKpis TEXT,
    demoStart DATE,
    demoTrades LONGTEXT,
    demoKpis TEXT,
    mq4StrategyFile VARCHAR(255),
    sqxStrategyFile VARCHAR(255)
);
drop table Strategies