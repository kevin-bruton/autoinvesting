CREATE TABLE Strategies (
    strategyName VARCHAR(255) NOT NULL PRIMARY KEY,
    magic BIGINT,
    symbols VARCHAR(255),
    timeframes VARCHAR(55),
    generationDate DATE,
    demoDate DATE,
    liveDate DATE,
    mq4StrategyFile VARCHAR(255),
    sqxStrategyFile VARCHAR(255)
);
