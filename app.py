import mysql.connector.pooling
from flask import *
import json

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # FLASK會將JSON資料的ASCII編碼
app.config["TEMPLATES_AUTO_RELOAD"] = True  # 修改templates會自動載入


db = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "TP_data",
    "pool_size": 8
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db)

# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")


@app.route("/booking")
def booking():
    return render_template("booking.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


""" 取得景點資料列表 """


@app.route("/api/attractions")
def attractions_data():
    page = int(request.args.get("page", 0))  # 預設0，整數格式
    keyword = request.args.get("keyword", "")
    try:
        total_records = get_total_records()
        total_records_with_keyword = get_total_records_with_keyword(keyword)
        data = get_attractions_data(
            page, keyword, total_records, total_records_with_keyword)
        # 回傳資料不要透過jsonify，排序會亂
        json_data = json.dumps(data)
        response = Response(
            json_data, content_type="application/json", status=200)
        return response
    except Exception:
        response = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(response), 500

# 取得所有資料總數量


def get_total_records():
    connection = connection_pool.get_connection()
    cursor = connection.cursor()

    total_records_query = """SELECT COUNT(id) FROM attractions"""
    cursor.execute(total_records_query)
    total_records = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return total_records

# 取得關鍵字篩選後的資料總數


def get_total_records_with_keyword(keyword):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()

    query = """
        SELECT COUNT(id)
        FROM attractions
        WHERE name LIKE %s OR mrt = %s
    """
    keyword_pattern = f"%{keyword}%"
    cursor.execute(query, (keyword_pattern, keyword))
    total_records = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return total_records


def get_attractions_data(page, keyword, total_records, total_records_with_keyword):
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    items_per_page = 12  # 一次顯示12筆
    offset = page * items_per_page  # 從第幾項開始顯示

    if keyword:  # 關鍵字搜尋
        query = """
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
                a.name LIKE %s OR a.mrt = %s
            GROUP BY
                a.id
            LIMIT %s, %s
        """
        keyword_pattern = f"%{keyword}%"
        cursor.execute(
            query, (keyword_pattern, keyword, offset, items_per_page))
        result = cursor.fetchall()

        # 已顯示筆數+應顯示筆數<可顯示總筆數，就會+1，反之代表超過可以顯示的數量
        if ((offset + items_per_page) < total_records_with_keyword):
            next_page = page + 1
        else:
            next_page = None

    else:  # 頁數搜尋
        query = """
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
            GROUP BY
                a.id
            LIMIT %s, %s
        """
        cursor.execute(query, (offset, items_per_page))
        result = cursor.fetchall()
        # 已顯示筆數+應顯示筆數<可顯示總筆數數，就會+1，反之代表超過可以顯示的數量
        if ((offset + items_per_page) < total_records):
            next_page = page + 1
        else:
            next_page = None

    data = []

    for row in result:
        images = row.pop("images").split(",")  # pop刪除"鍵"，返回"值"，轉換成列表
        row["images"] = images
        row["lat"] = float(row["lat"])
        row["lng"] = float(row["lng"])
        data.append(row)

    cursor.close()
    connection.close()

    return {
        "nextPage": next_page,
        "data": data
    }


""" 根據景點編號取得景點資料 """


@app.route("/api/attractions/<int:attractionId>")
def get_attraction(attractionId):
    try:
        attraction = get_attraction_data(attractionId)
        if attraction is not None:
            json_data = json.dumps(attraction)
            response = Response(
                json_data, content_type="application/json", status=200)
            return response
        else:
            error_response = {
                "error": True,
                "message": "景點編號不正確"
            }
            return jsonify(error_response), 400
    except Exception:
        error_response = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(error_response), 500


def get_attraction_data(attraction_id):
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
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
            a.id = %s
    """

    cursor.execute(query, (attraction_id,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result["id"] != None:
        images = result.pop("images").split(",")
        result["images"] = images
        result["lat"] = float(result["lat"])
        result["lng"] = float(result["lng"])
        return {"data": result}
    else:
        return None


""" 取得捷運站名稱列表 """


@app.route("/api/mrts")
def get_mrts():
    try:
        mrts = get_mrt_names()
        return jsonify(mrts), 200
    except Exception:
        error_response = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(error_response), 500


def get_mrt_names():
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT a.mrt 
        FROM attractions a
        GROUP BY a.mrt
        ORDER BY COUNT(*) DESC, a.mrt
    """

    cursor.execute(query)
    result = cursor.fetchall()

    mrts = []
    count = 0
    for row in result:
        if row["mrt"] is not None:
            mrts.append(row["mrt"])
            count += 1
            if count >= 40:
                break

    cursor.close()
    connection.close()

    return {"data": mrts}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
