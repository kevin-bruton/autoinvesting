CREATE TABLE Users (
    userId int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username varchar(55),
    passwd varchar(55),
    email varchar(55),
    firstName varchar(55),
    lastName varchar(55),
    city varchar(55),
    country varchar(55),
    accountType varchar(55) DEFAULT 'investor',
    demoKey varchar(55),
    demoSubscriptions text DEFAULT '[]'
    demoAccountNumber bigint,
    liveKey varchar(55),
    liveSubscriptions text DEFAULT '[]',
    liveAccountNumber bigint
);

