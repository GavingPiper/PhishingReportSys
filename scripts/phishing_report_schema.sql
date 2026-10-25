-- -----------------------------------------------------
-- Schema phishing-db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS phishing_db
DEFAULT CHARACTER SET utf8;

USE phishing_db;

-- -----------------------------------------------------
-- Table Clients
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS Clients (
    clientID INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    phoneNumber CHAR(10) NULL,
    PRIMARY KEY (clientID)
);

-- -----------------------------------------------------
-- Table Emails
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS Emails (
    emailID INT NOT NULL AUTO_INCREMENT,
    clientID INT NOT NULL,
    sender VARCHAR(255) NULL,
    recipient VARCHAR(255) NULL,
    body TEXT NULL,
    createdOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (emailID),
    FOREIGN KEY (clientID)
        REFERENCES Clients (clientID)
);