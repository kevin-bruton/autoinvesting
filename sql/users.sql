CREATE TABLE Users (
    username varchar(55) NOT NULL PRIMARY KEY,
    passwd varchar(55),
    email varchar(55),
    firstName varchar(55),
    lastName varchar(55),
    city varchar(55),
    country varchar(55),
    accountType varchar(55) DEFAULT 'investor'
);

