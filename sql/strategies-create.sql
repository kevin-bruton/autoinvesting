CREATE TABLE Strategies (
    strategyName VARCHAR(255) NOT NULL,
    magic BIGINT NOT NULL,
    symbols VARCHAR(255) NOT NULL,
    timeframes VARCHAR(55) NOT NULL,
    btStart DATE,
    btEnd DATE,
    btDeposit FLOAT(9),
    btTrades LONGTEXT,
    btKpis TEXT,
    demoStart DATE,
    demoTrades LONGTEXT,
    demoKpis TEXT,
    mq4StrategyFile VARCHAR(255),
    sqxStrategyFile VARCHAR(255),
    description TEXT,
    workflow VARCHAR(255),
    PRIMARY KEY (magic)
);
