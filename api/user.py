from flask import *
from model.JWT import validate_token
from model.user import is_valid_name, is_valid_email, is_valid_password, signup_check, signup_new_user, signin_check, save_token, delete_token, generate_token


# 使用 Blueprint 創建路由
user_bp = Blueprint('user', __name__)


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

    # 從資料庫中取得使用者的相關資訊
    member_data = signin_check(email, password)

    if member_data is None:
        return jsonify({"error": True, "message": "email或密碼輸入錯誤"})
    else:
        member_id = member_data[0]
        member_name = member_data[1]

        # 建立token
        token = generate_token(member_id, member_name, email)

        # 將新建立的token存入資料庫
        save_token(member_id, token)
        return jsonify({"token": token})


""" 取得登入會員資訊 """


@user_bp.route("/api/user/auth", methods=["GET"])
def get_user_inf():
    token_data = validate_token()
    if token_data is not None:
        id = token_data.get("id")
        name = token_data.get("name")
        email = token_data.get("email")
        return jsonify({"data": {
            "id": id,
            "name": name,
            "email": email
        }})
    else:
        return jsonify(None)


""" 登出 """


@user_bp.route("/api/user/auth", methods=["DELETE"])
def logout():
    token = request.headers.get("Authorization")
    token = token.replace("Bearer ", "")
    if delete_token(token):
        return jsonify({"type": "success", "message": "登出成功"})
    else:
        return jsonify({"type": "error", "message": "登出失敗"})
