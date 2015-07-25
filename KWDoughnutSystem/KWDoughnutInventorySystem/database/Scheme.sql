USE DoughnutSystem;
CREATE TABLE usr
(
    ID INT NOT NULL AUTO_INCREMENT,
    usrName NVARCHAR(20),
    usrPsd VARCHAR(256),
    PRIMARY KEY (ID)
);
CREATE TABLE priceScheme
(
    ID INT NOT NULL AUTO_INCREMENT,
    boxPrice FLOAT(5,2),
    doughnutPrice FLOAT(4,2),
    PRIMARY KEY (ID)
);
CREATE TABLE transHistory
(
    ID INT NOT NULL AUTO_INCREMENT,
    schemeID INT,
    sellerID INT,
    timeSold TIMESTAMP,
    doughnutsSold INT NOT NULL DEFAULT 0,
    boxesSold INT NOT NULL DEFAULT 0,
    deleted BIT NOT NULL DEFAULT 0,
    deferredPayment BIT NOT NULL DEFAULT 0,
    deletedUsrInit NVARCHAR(20),
    PRIMARY KEY (ID),
    FOREIGN KEY (schemeID) REFERENCES priceScheme(ID),
    FOREIGN KEY (sellerID) REFERENCES usr(ID)
);
CREATE TABLE donation
(
    ID INT NOT NULL AUTO_INCREMENT,
    timeDonated TIMESTAMP,
    Amount FLOAT(9,2),
    Donor NVARCHAR(100),
    deleted BIT NOT NULL DEFAULT 0,
    PRIMARY KEY(ID)
);
INSERT INTO priceScheme VALUES (1, 10.00, 1.00);
INSERT INTO transHistory VALUES (0, 1, 1, NOW(), 0, 0, 0, 0, 'admin');
INSERT INTO priceScheme VALUES (0, 0, 0);