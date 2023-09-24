from flask import *
from model.database import connection_pool, execute_query
from datetime import datetime, timedelta
import re
import jwt  # pip install pyjwt

# 使用 Blueprint 創建路由
user_bp = Blueprint('user', __name__)


header = {
    "alg": "HS256",  # 簽名技術
    "typ": "JWT"  # 類型
}


""" 註冊 """
# https://www.cnblogs.com/luo630/p/9062739.htmls


@user_bp.route("/api/user", methods=["POST"])
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


@user_bp.route("/api/user/auth", methods=["PUT"])
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

        # 使用 current_app 取得 SECRET_KEY
        secret_key = current_app.config['SECRET_KEY']

        # 建立token
        payload = {'id': member_id,
                   'name': member_name,
                   'email': email,
                   'exp': datetime.utcnow() + timedelta(days=7)}     # UTCNOW為當前時間，設定過期時間為七天後
        token = jwt.encode(
            payload, secret_key, algorithm="HS256", headers=header)
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


""" ---------------------------Token檢查--------------------------- """
""" 驗證token """


@user_bp.route("/api/user/auth", methods=["GET"])
def verify_token():
    # 取得前端傳過來的token
    token = request.headers.get("Authorization")
    token = token.replace("Bearer ", "")

    try:
        # 使用 current_app 取得 SECRET_KEY
        secret_key = current_app.config['SECRET_KEY']

        decoded_token = jwt.decode(
            token, secret_key, algorithms=["HS256"])
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


@user_bp.route("/api/user/auth", methods=["DELETE"])
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
