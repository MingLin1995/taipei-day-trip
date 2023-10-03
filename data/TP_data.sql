SHOW DATABASES; 
/*CREATE DATABASE TP_data; */

USE TP_data; 
SHOW TABLES;

/*DROP DATABASE TP_data; */

CREATE TABLE attractions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(255),
    description TEXT, /*可以存6.4萬個字元*/
    address VARCHAR(255),
    transport TEXT,
    mrt VARCHAR(255),
    lat DECIMAL(9, 6), /*顯示到小數點六位數，總共最多九位數*/
    lng DECIMAL(9, 6)
);
SELECT * FROM attractions;

CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attraction_id INT,
    image_url VARCHAR(255),
    FOREIGN KEY (attraction_id) REFERENCES attractions(id)
);
SELECT * FROM images;

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
    FOREIGN KEY (member_id) REFERENCES member(id),
	status INT NOT NULL DEFAULT 1
);
SELECT * FROM booking;

CREATE TABLE orders (
    id INT  PRIMARY KEY AUTO_INCREMENT,
    number VARCHAR(255) NOT NULL,
	name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL ,
    phone VARCHAR(255) NOT NULL,
	booking_id INT NOT NULL
);

SELECT * FROM orders;

/*DROP table booking;*/
