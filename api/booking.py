from flask import *
from model.JWT import validate_token
from model.database import execute_query
import requests  # pip install requests
import random
from decouple import config  # pip install python-decouple 讀取.env


# 使用 Blueprint 創建路由
booking_bp = Blueprint('booking', __name__)

""" 新增訂單 """


@booking_bp.route('/api/booking', methods=['POST'])
def booking():
    try:
        token_data = validate_token()
        if token_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        booking_data = request.get_json()

        if create_booking(token_data, booking_data):
            return jsonify({"ok": True}), 200
        else:
            return jsonify({"error": True, "message": "建立失敗，資料輸入不正確"}), 400
    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500


def create_booking(token_data, booking_data):
    member_id = token_data.get("id")
    attractionId = booking_data.get("attractionId")
    date = booking_data.get("date")
    time = booking_data.get("time")
    price = booking_data.get("price")

    if None in (member_id, attractionId, date, time, price):
        return False

    # 是否已經存在訂單
    existing_booking_sql = "SELECT id FROM booking WHERE member_id = %s"
    existing_booking_params = (member_id,)
    existing_booking = execute_query(
        existing_booking_sql, existing_booking_params, fetch_one=True)

    if existing_booking:
        # 存在的話先刪除
        delete_booking_sql = "DELETE FROM booking WHERE id = %s"
        delete_booking_params = (existing_booking[0],)
        execute_query(delete_booking_sql,
                      delete_booking_params, commit=True)
        reset_id = "ALTER TABLE booking AUTO_INCREMENT = 1"
        execute_query(reset_id, commit=True)

    # 新增訂單
    sql = "INSERT INTO booking (member_id, attractionId, date, time, price) VALUES (%s, %s, %s, %s, %s)"
    values = (member_id, attractionId, date, time, price)
    execute_query(sql, values, commit=True)

    return True


""" 取得訂單資料 """


@booking_bp.route('/api/booking', methods=['GET'])
def get_booking_inf():
    try:
        token_data = validate_token()
        if token_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        booking_inf = find_booking_inf(token_data)

        return jsonify(booking_inf), 200

    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500


def find_booking_inf(token_data):
    member_id = token_data.get("id")

    # 搜尋訂單資料
    sql = """
        SELECT b.date, b.time, b.price, a.id, a.name, a.address, i.image_url
        FROM booking b
        JOIN attractions a ON b.attractionId = a.id
        LEFT JOIN images i ON b.attractionId = i.attraction_id
        WHERE b.member_id = %s AND b.status = 1
    """

    result = execute_query(sql, (member_id,))

    if result:
        data = result[0]
        date = data[0]
        time = data[1]
        price = data[2]

        attraction_data = {
            "id": data[3],
            "name": data[4],
            "address": data[5],
            "image": data[6]
        }

        booking_data = {
            "data": {
                "attraction": attraction_data,
                "date": str(date),
                "time": time,
                "price": price
            }
        }

        return booking_data

    else:
        return {"data": None}


""" 刪除訂單 """


@booking_bp.route('/api/booking', methods=['DELETE'])
def del_booking():
    try:
        token_data = validate_token()
        member_id = token_data.get("id")

        if token_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        update_booking_status(member_id)  # 狀態改為0，代表刪除
        return jsonify({"ok": True}), 200
    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500


""" 訂單付款 """


@booking_bp.route('/api/orders', methods=['POST'])
def corder():
    try:
        token_data = validate_token()
        if token_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
        order_data = request.get_json()

        # 建立訂單號碼
        order_number = create_order(token_data, order_data)
        if order_number:

            # 將資訊傳送到TapPay伺服器
            member_id = token_data.get("id")

            payment_info = process_payment(order_data, order_number, member_id)

            # 將訂單狀態回傳給前端
            if payment_info:
                response_data = {
                    "data": payment_info
                }
                return jsonify(response_data), 200
        else:
            return jsonify({"error": True, "message": "建立失敗，資料輸入不正確"}), 400
    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500


def create_order(token_data, order_data):
    # 查詢booking_id
    member_id = token_data.get("id")
    sql = "SELECT id FROM booking WHERE member_id = %s"
    booking_id = execute_query(
        sql, (member_id,), fetch_one=True)

    while True:  # 確保獨一無二
        neme = order_data.get("order").get("contact").get("name")
        email = order_data.get("order").get("contact").get("email")

        # 建立order_number
        date = order_data.get("order").get("trip").get("date").replace("-", "")
        phone = order_data.get("order").get("contact").get("phone")
        random_digits = str(random.randint(10000, 99999))  # 生成五位亂數
        number = date + phone[-3:] + random_digits

        # 檢查number是否已存在於orders資料表中
        check_sql = "SELECT COUNT(*) FROM orders WHERE number = %s"
        count = execute_query(
            check_sql, (number,), fetch_one=True)

        # 如果number不存在，則可以建立number
        if count[0] == 0:
            insert_order_sql = "INSERT INTO orders (number, name, email, phone, booking_id) VALUES (%s, %s, %s, %s, %s)"
            insert_order_params = (number, neme, email,
                                   phone, booking_id[0])  # booking_id為tuple

            execute_query(insert_order_sql,
                          insert_order_params, commit=True)
            return number


""" TapPay """
# 適用於 TapPay 的測試環境或正式環境 URL
TAPPAY_API_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
PARTNER_KEY = config('PARTNER_KEY')
MERCHANT_ID = config('MERCHANT_ID')

# 將資訊傳送到TapPay伺服器


def process_payment(order_data, order_number, member_id):

    prime = order_data.get('prime')
    details = "TapPay Test"
    order_amount = order_data.get("order").get("price")
    phone_number = order_data.get("order").get("contact").get("phone")
    name = order_data.get("order").get("contact").get("name")
    email = order_data.get("order").get("contact").get("email")

    # 整理成參考文件的格式
    tappay_request_data = {
        "prime": prime,
        "partner_key": PARTNER_KEY,
        "merchant_id": MERCHANT_ID,
        "details": details,
        "amount": order_amount,
        "cardholder": {
            "phone_number": phone_number,
            "name": name,
            "email": email,

        },
        "remember": True  # 可選是否記憶卡號
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": PARTNER_KEY
    }

    try:
        response = requests.post(
            TAPPAY_API_URL, json=tappay_request_data, headers=headers)
        if response.status_code == 200:
            payment_result = response.json()
            if payment_result.get('status') == 0:  # 狀態為0表示成功
                # 支付成功，更新訂單狀態改為0
                update_booking_status(member_id)

                payment_info = {
                    "number": order_number,
                    "payment": {
                        "status": 0,
                        "message": "付款成功"
                    }
                }
                return payment_info

    except Exception as e:
        return jsonify(message='Internal server error', error=str(e)), 500


def update_booking_status(member_id):
    sql_update = "UPDATE booking SET status = 0 WHERE member_id = %s"
    update_params = (member_id,)
    execute_query(sql_update,
                  update_params, commit=True)


# 將config傳送到前端
@booking_bp.route('/api/config', methods=['GET'])
def get_config():
    APP_ID = config("APP_ID")
    APP_KEY = config("APP_KEY")
    config_data = {
        "APP_ID": APP_ID,
        "APP_KEY": APP_KEY
    }
    return jsonify(config_data)
