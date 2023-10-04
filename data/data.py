import json
from model.database import execute_query

with open("taipei-attractions.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
results = data['result']['results']

""" 先確認所需資訊 """
""" print(results[0]["name"])  # 景點名稱
print(results[0]["CAT"])  # 景點類別
print(results[0]["description"])  # 景點介紹
print(results[0]["address"])  # 景點位置（要排除"空白"符號，顯示完整地址）
print(results[0]["direction"])  # 前往方式
print(results[0]["MRT"])  # 鄰近捷運站 （陽明山有none）
print(results[0]["latitude"])  # 緯度
print(results[0]["longitude"])  # 經度
print(results[0]["file"])  # 圖片網址（要整裡全部的網址） """

""" 整理資料 """
""" print(results[1]["address"].replace(" ", ""))

file = results[0]["file"]
# 全部轉換成小寫，用https://去分割
image_links = file.lower().split('https://')[1:]  # 以 https:// 分隔，去掉第一個空元素
# 補上https://，並篩選.jpg、.png結尾的資料
image_urls = ['https://' +
              link for link in image_links if link.endswith(('.jpg', '.png'))] """

""" 存取資料 """
attractions_data = []

for result in results:
    file = result["file"]
    image_links = file.lower().split('https://')[1:]
    image_urls = ['https://' +
                  link for link in image_links if link.endswith(('.jpg', '.png'))]

    attraction = {
        "name": result["name"],
        "CAT": result["CAT"],
        "description": result["description"],
        "address": result["address"].replace(" ", ""),
        "direction": result["direction"],
        "MRT": result["MRT"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "file": image_urls
    }
    attractions_data.append(attraction)

# print(attractions_data[1]["file"][7])  # 確定資料正確


for attraction in attractions_data:
    insert_query = "INSERT INTO attractions (name, category, description, address, transport, mrt, lat, lng) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (attraction["name"], attraction["CAT"], attraction["description"], attraction["address"],
              attraction["direction"], attraction["MRT"], attraction["latitude"], attraction["longitude"])
    execute_query(insert_query, values, commit=True)

    # 取得最後插入資料的主鍵值
    attraction_id = execute_query("SELECT LAST_INSERT_ID()", fetch_one=True)[0]

    for image_url in attraction["file"]:
        insert_image_query = "INSERT INTO images (attraction_id, image_url) VALUES (%s, %s)"
        image_values = (attraction_id, image_url)
        execute_query(insert_image_query, image_values, commit=True)
