SHOW DATABASES; 
/*CREATE DATABASE TP_data; */

USE TP_data; 
SHOW TABLES;

# 刪除刪除刪除不要誤點
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

/*頁數查詢*/
SELECT
    a.id,
    a.name,
    a.category,
    a.description,
    a.address,
    a.transport,
    a.mrt,
    a.lat,
    a.lng,
    GROUP_CONCAT(i.image_url) AS images /*將所有網址合併成一個字串，用","分隔*/
FROM
    attractions a
JOIN
    images i ON a.id = i.attraction_id
GROUP BY
    a.id /*依照id去分組，再將圖片網址合併*/
LIMIT 24, 12; /*從結果的index 24開始(第25筆)取資料，顯示12筆*/

/*關鍵字查詢*/
SELECT
	a.id,
	a.name,
	a.category,
	a.description,
	a.address,
	a.transport,
	a.mrt,
	a.lat,
	a.lng,
	GROUP_CONCAT(i.image_url) AS images
FROM
	attractions a
JOIN
	images i ON a.id = i.attraction_id
WHERE
	a.name LIKE '%北%' OR a.mrt = '北' /*模糊景點名稱或完整捷運名稱*/
GROUP BY 
	a.id 
LIMIT 12,12; /*總共16筆，12,0的時候，會有下一頁(還有4筆)*/

/*景點編號*/
SELECT
    a.id,
    a.name,
    a.category,
    a.description,
    a.address,
    a.transport,
    a.mrt,
    a.lat,
    a.lng,
    GROUP_CONCAT(i.image_url) AS images
FROM
    attractions a
JOIN
    images i ON a.id = i.attraction_id
WHERE
    a.id = '45';


/*捷運查詢*/
/*先查詢各個捷運站出現的次數*/
SELECT a.mrt, COUNT(*) AS num_attractions 
FROM attractions a
GROUP BY a.mrt
ORDER BY num_attractions DESC, a.mrt; /*數量大到小，捷運名稱筆畫小到大*/

/*降冪排列*/
SELECT a.mrt 
FROM attractions a
GROUP BY a.mrt
ORDER BY COUNT(*) DESC, a.mrt; 






