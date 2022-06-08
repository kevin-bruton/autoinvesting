CREATE TABLE Users (
    userId int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username varchar(55),
    passwd varchar(55),
    email varchar(55),
    firstName varchar(55),
    lastName varchar(55),
    city varchar(55),
    country varchar(55)
);

INSERT INTO Users (username,passwd,firstName,lastName,city,country,email)
VALUES ('user123', 'secret', 'joe.blow@mail.com', 'Joe', 'Blow', 'Sydney', 'Australia');
