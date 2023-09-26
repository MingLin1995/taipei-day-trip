SHOW DATABASES; 
CREATE DATABASE website; 

USE website; 
SHOW TABLES;

CREATE TABLE member (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

SELECT * FROM member;

CREATE TABLE token (
    id INT  PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    token VARCHAR(1000) NOT NULL,
    time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES member(id)
);

SELECT * FROM token;

CREATE TABLE booking (
    id INT  PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    attractionId INT NOT NULL,
    date DATE,
    time VARCHAR(255),
    price DECIMAL(10),
    FOREIGN KEY (member_id) REFERENCES member(id)
);

SELECT * FROM booking;

#DROP TABLE booking;
