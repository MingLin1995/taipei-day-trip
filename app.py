import mysql.connector.pooling
from flask import *
import json
import re
import jwt  # pip install pyjwt
from datetime import datetime, timedelta
from flask_cors import CORS  # 處理跨域問題 pip install flask-cors


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # FLASK會將JSON資料的ASCII編碼
app.config["TEMPLATES_AUTO_RELOAD"] = True  # 修改templates會自動載入
CORS(app)  # 啟用CORS

header = {
    "alg": "HS256",  # 簽名技術
    "typ": "JWT"  # 類型
}

app.config['SECRET_KEY'] = "密鑰可以是任何的字串，但是不要告訴別人"

db_TP_data = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "TP_data",
    "pool_size": 8
}
connection_pool_TP_data = mysql.connector.pooling.MySQLConnectionPool(
    **db_TP_data)

db_member = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "website",
    "pool_size": 8
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_member)


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
        data = get_attractions_data(page, keyword)
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


# 取得景點資料(頁數搜尋以及關鍵字搜尋)


def get_attractions_data(page, keyword):
    connection = connection_pool_TP_data.get_connection()
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
        cursor.execute(query, (keyword_pattern, keyword,
                       offset, items_per_page+1))
        result = cursor.fetchall()

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
        cursor.execute(query, (offset, items_per_page+1))
        result = cursor.fetchall()

    # 用多查詢一筆的方式去判斷是否還有下一頁
    next_page = None
    if len(result) > items_per_page:
        next_page = page + 1
        result = result[:items_per_page]  # 只返回前12条数据

    data = []

    for row in result:
        attraction_id = row["id"]
        images = get_attraction_images(attraction_id, cursor)
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


def get_basic_attraction_info(attraction_id, cursor):
    # 取得基本資訊
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
            a.lng
        FROM
            attractions a
        WHERE
            a.id = %s
    """

    cursor.execute(query, (attraction_id,))
    result = cursor.fetchone()
    return result


def get_attraction_images(attraction_id, cursor):
    # 圖片URL
    image_query = """
    SELECT
        i.image_url
    FROM
        images i
    WHERE
        i.attraction_id = %s
    """
    cursor.execute(image_query, (attraction_id,))
    image_results = cursor.fetchall()
    images = [image_result['image_url'] for image_result in image_results]
    return images


def get_attraction_data(attraction_id):
    connection = connection_pool_TP_data.get_connection()
    cursor = connection.cursor(dictionary=True)

    # 取得基本資訊
    basic_info = get_basic_attraction_info(attraction_id, cursor)

    if basic_info:
        # 取得圖片資訊
        images = get_attraction_images(attraction_id, cursor)

        # 合并结果
        basic_info["images"] = images
        basic_info["lat"] = float(basic_info["lat"])
        basic_info["lng"] = float(basic_info["lng"])

        cursor.close()
        connection.close()

        return {"data": basic_info}
    else:
        cursor.close()
        connection.close()
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
    connection = connection_pool_TP_data.get_connection()
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


""" 註冊 """
# https://www.cnblogs.com/luo630/p/9062739.htmls


@app.route("/api/user", methods=["POST"])
def signup():
    data = request.json  # 前端以 JSON 格式提交數據
    name = data["name"]
    email = data["email"]
    password = data["password"]
    try:
        # 判斷是否為空白欄位
        # 使用.strip()方法刪除首、尾空白字符，然後進行比較(否則還是可以輸入空白)
        if name.strip() == "" or email.strip() == "" or password.strip() == "":
            response = {"error": True, "message": "註冊欄位不得為空白"}
            return jsonify(response), 400
        # 驗證格式
        if not is_valid_name(name):
            response = {"error": True, "message": "姓名格式不正確，請輸入中文或英文，至少兩個字元"}
            return jsonify(response), 400

        if not is_valid_email(email):
            response = {"error": True, "message": "email格式不正確，請輸入正確的email"}
            return jsonify(response), 400

        if not is_valid_password(password):
            response = {"error": True,
                        "message": "密碼格式不正確，請輸入英文或數字，至少六個字元"}
            return jsonify(response), 400

        if signup_check(email) is None:
            signup_new_user(name, email, password)
            return jsonify({"ok": True}), 200
        else:
            return jsonify({"error": True, "message": "email已經被註冊"}), 400
    except Exception:
        response = {"error": True,
                    "message": "伺服器內部錯誤"}
        return jsonify(response), 500


""" 檢查帳號是否註冊過 """


def signup_check(email):
    sql = "SELECT * FROM member WHERE email = %s"
    return execute_query(connection_pool, sql, (email,), fetch_one=True)


""" 新註冊姓名、帳號、密碼 """


def signup_new_user(name, email, password):
    sql = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
    execute_query(connection_pool, sql,
                  (name, email, password), commit=True)


""" 登入"""


@app.route("/api/user/auth", methods=["PUT"])
def signin():
    data = request.json
    email = data["email"]
    password = data["password"]
    # 判斷是否為空白欄位
    if email.strip() == "" or password.strip() == "":
        response = {"error": True, "message": "登入欄位不得為空白"}
        return jsonify(response)

    # 驗證格式
    if not is_valid_email(email):
        response = {"error": True, "message": "email格式不正確，請輸入正確的email"}
        return jsonify(response)

    if not is_valid_password(password):
        response = {"error": True,
                    "message": "密碼格式不正確，請輸入英文或數字，至少六個字元"}
        return jsonify(response)

    member_data = signin_check(email, password)

    if member_data is None:
        return jsonify({"error": True, "message": "email或密碼輸入錯誤"})
    else:
        # 從資料庫中取得使用者的相關資訊
        member_id = member_data[0]
        member_name = member_data[1]
        # 建立token
        payload = {'id': member_id,
                   'name': member_name,
                   'email': email,
                   'exp': datetime.utcnow() + timedelta(days=7)}     # UTCNOW為當前時間，設定過期時間為七天後
        token = jwt.encode(
            payload, app.config['SECRET_KEY'], algorithm="S256", headers=header)
        # 將新建立的token存入資料庫
        save_token(member_id, token)
        return jsonify({"token": token})


""" 檢查帳號密碼是否正確 """


def signin_check(email, password):
    sql = "SELECT * FROM member WHERE email = %s AND password = %s"
    return execute_query(connection_pool, sql, (email, password), fetch_one=True)


""" 將token存入資料庫 """


def save_token(member_id, token):
    connection = connection_pool.get_connection()
    cur = connection.cursor()

    # 檢查是否已存在該 member_id 的 token 記錄
    find_token_sql = "SELECT member_id FROM token WHERE member_id = %s"
    cur.execute(find_token_sql, (member_id,))
    old_token_id = cur.fetchone()

    # 如果有 token 刪除舊的 token 記錄
    if old_token_id:
        delete_token_sql = "DELETE FROM token WHERE member_id = %s"
        cur.execute(delete_token_sql, (old_token_id[0],))
        reset_id = "ALTER TABLE token AUTO_INCREMENT = 1"
        cur.execute(reset_id)

    # 如果沒有 token ，則新增 token到資料庫
    insert_token_sql = "INSERT INTO token (member_id, token) VALUES (%s, %s)"
    cur.execute(insert_token_sql, (member_id, token))
    connection.commit()

    cur.close()
    connection.close()


""" ---------------------驗證資料格式--------------------------------- """
# re.match(pattern(匹配標準), string(要匹配的字串))


def is_valid_name(name):
    # 姓名格式驗證，只能是中文、英文，至少兩個字元
    name_pattern = r'^[\u4e00-\u9fa5A-Za-z\s]{2,}$'
    return re.match(name_pattern, name)


def is_valid_email(email):
    # email格式驗證
    email_pattern = r'\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}'
    return re.match(email_pattern, email)


def is_valid_password(password):
    # 密碼格式驗證，只能是英文或數字，至少六個字元
    password_pattern = r'^[A-Za-z0-9]{6,}$'
    return re.match(password_pattern, password)


""" ---------------------會員系統簡化資料庫溝通流程------------------------ """


def execute_query(connection_pool, sql, parameter=None, fetch_one=False, commit=False):
    connection = connection_pool.get_connection()
    cur = connection.cursor()

    cur.execute(sql, parameter)

    if fetch_one:
        data = cur.fetchone()
    else:
        data = cur.fetchall()

    if commit:
        connection.commit()

    cur.close()
    connection.close()
    return data


""" ---------------------------Token檢查--------------------------- """
""" 驗證token """


@app.route("/api/user/auth", methods=["GET"])
def verify_token():
    # 取得前端傳過來的token
    token = request.headers.get("Authorization")
    token = token.replace("Bearer ", "")

    try:
        decoded_token = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=["HS256"])
        id = decoded_token.get("id")

        if check_token(id, token):
            name = decoded_token.get("name")
            email = decoded_token.get("email")
            return jsonify({"data": {
                "id": id,
                "name": name,
                "email": email
            }})
        else:
            return jsonify(None)
    except jwt.ExpiredSignatureError:
        return jsonify(None)
    except jwt.DecodeError:
        return jsonify(None)


def check_token(id, token):
    sql = "SELECT token FROM token WHERE member_id = %s"
    result = execute_query(connection_pool, sql, (id,), fetch_one=True)
    # 如果有token且與回傳token相符
    if result and result[0] == token:
        return True
    else:
        return False


""" 登出 """


@app.route("/api/user/auth", methods=["DELETE"])
def logout():
    token = request.headers.get("Authorization")
    token = token.replace("Bearer ", "")
    if delete_token(token):
        return jsonify({"type": "success", "message": "登出成功"})
    else:
        return jsonify({"type": "error", "message": "登出失敗"})


def delete_token(token):
    try:
        # 先解除刪除的安全機制
        sql_1 = "set sql_safe_updates=0"
        execute_query(connection_pool, sql_1, commit=True)

        # 執行刪除
        sql_2 = "DELETE FROM token WHERE token = %s"
        execute_query(connection_pool, sql_2, (token,), commit=True)
        reset_id = "ALTER TABLE token AUTO_INCREMENT = 1"
        execute_query(connection_pool, reset_id, commit=True)

        # 恢復安全機制
        sql_3 = "set sql_safe_updates=1"
        execute_query(connection_pool, sql_3, commit=True)

        return True
    except Exception as e:
        print("刪除 token 時發生錯誤:", str(e))
        return False


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
