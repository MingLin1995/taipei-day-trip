
from model.database import execute_query
import re
import jwt
from datetime import datetime, timedelta
from flask import current_app


""" 檢查帳號是否註冊過 """


def signup_check(email):
    sql = "SELECT * FROM member WHERE email = %s"
    return execute_query(sql, (email,), fetch_one=True)


""" 新註冊姓名、帳號、密碼 """


def signup_new_user(name, email, password):
    sql = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
    execute_query(sql,
                  (name, email, password), commit=True)


""" 檢查帳號密碼是否正確 """


def signin_check(email, password):
    sql = "SELECT * FROM member WHERE email = %s AND password = %s"
    return execute_query(sql, (email, password), fetch_one=True)


""" 登出 """


def delete_token(token):
    try:
        # 先解除刪除的安全機制
        sql_1 = "set sql_safe_updates=0"
        execute_query(sql_1, commit=True)

        # 執行刪除
        sql_2 = "DELETE FROM token WHERE token = %s"
        execute_query(sql_2, (token,), commit=True)
        reset_id = "ALTER TABLE token AUTO_INCREMENT = 1"
        execute_query(reset_id, commit=True)

        # 恢復安全機制
        sql_3 = "set sql_safe_updates=1"
        execute_query(sql_3, commit=True)

        return True
    except Exception as e:
        print("刪除 token 時發生錯誤:", str(e))
        return False


""" 將token存入資料庫 """


def save_token(member_id, token):
    # 檢查是否已存在該 member_id 的 token 記錄
    find_token_sql = "SELECT member_id FROM token WHERE member_id = %s"
    old_token_id = execute_query(
        find_token_sql, (member_id,), fetch_one=True)

    # 如果有 token 刪除舊的 token 記錄
    if old_token_id:
        delete_token_sql = "DELETE FROM token WHERE member_id = %s"
        execute_query(delete_token_sql,
                      (old_token_id[0],), commit=True)
        reset_id = "ALTER TABLE token AUTO_INCREMENT = 1"
        execute_query(reset_id, commit=True)

    # 如果沒有 token ，則新增 token 到資料庫
    insert_token_sql = "INSERT INTO token (member_id, token) VALUES (%s, %s)"
    execute_query(insert_token_sql,
                  (member_id, token), commit=True)


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


""" 建立token """
header = {
    "alg": "HS256",  # 簽名技術
    "typ": "JWT"  # 類型
}


def generate_token(member_id, member_name, email):
    # 使用 current_app 取得 SECRET_KEY
    secret_key = current_app.config['SECRET_KEY']

    # 建立 token 的 payload
    payload = {
        'id': member_id,
        'name': member_name,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)  # UTCNOW為當前時間，設定過期時間為七天後
    }

    # 使用 jwt.encode 生成 token
    token = jwt.encode(payload, secret_key, algorithm="HS256", headers=header)
    return token
