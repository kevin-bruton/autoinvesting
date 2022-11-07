CREATE TABLE Strategies (
    magic BIGINT NOT NULL,
    strategyName VARCHAR(255) NOT NULL,
    symbols VARCHAR(255) NOT NULL,
    timeframes VARCHAR(55) NOT NULL,
    description TEXT,
    workflow VARCHAR(255),
    PRIMARY KEY (magic)
);
