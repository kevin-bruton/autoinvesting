CREATE TABLE Strategies (
    strategyName VARCHAR(255) NOT NULL PRIMARY KEY,
    sqxName VARCHAR(255),
    magic INT,
    symbols VARCHAR(255),
    timeframe VARCHAR(55),
    generationDate DATE,
    demoDate DATE,
    liveDate DATE
);

INSERT INTO Strategies (strategyName, sqxName, magic, symbols, timeframe, generationDate, demoDate, liveDate)
VALUES ('superBot', 'WS30_H1_3.15.2', 202206101, 'WS30', 'H1', '2022-06-10', '2022-06-10', NULL);
