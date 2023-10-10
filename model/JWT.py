from flask import *
from model.database import execute_query
import jwt  # pip install pyjwt


def validate_token():
    # 取得前端傳過來的token
    token = request.headers.get("Authorization")
    token = token.replace("Bearer ", "")

    try:
        # 使用 current_app 取得 SECRET_KEY
        secret_key = current_app.config['SECRET_KEY']

        # 解碼
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        id = decoded_token.get("id")

        if check_token(id, token):
            return decoded_token  # 回傳解碼後的token
    except jwt.ExpiredSignatureError:  # 過期
        pass
    except jwt.DecodeError:  # 解碼錯誤
        pass

    return None  # Token 驗證失敗或是過期


def check_token(id, token):
    sql = "SELECT token FROM token WHERE member_id = %s"
    result = execute_query(sql, (id,), fetch_one=True)
    # 如果有token且與回傳token相符
    if result and result[0] == token:
        return True
    else:
        return False
