from model.database import execute_query
import random
import requests  # pip install requests
from model.booking import update_booking_status
from decouple import config  # pip install python-decouple 讀取.env

""" 訂單付款 """


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
            else:
                return {"error": True, "message": "付款失敗"}

    except Exception as e:
        return jsonify(message='Internal server error', error=str(e)), 500


""" 取得預訂、訂單資訊 """


def get_order_info(order_number):
    sql = "SELECT * FROM orders WHERE number = %s"
    order_data = execute_query(sql, (str(order_number),), fetch_one=True)
    return order_data


def get_booking_info(order_data):
    sql = "SELECT * FROM booking WHERE id = %s"
    booking_data = execute_query(
        sql, (order_data,), fetch_one=True)
    return booking_data


def get_attraction_info(attraction_id):
    sql = """
        SELECT a.name, a.address, i.image_url
        FROM attractions AS a
        LEFT JOIN images AS i ON a.id = i.attraction_id
        WHERE a.id = %s
    """
    attraction_data = execute_query(sql, (attraction_id,))
    return attraction_data


""" 建立訂單資訊 """


def build_order_info(order_number, booking_data, attraction_data, order_data):
    order_info = {
        "number": str(order_number),
        "price": int(booking_data[5]),
        "trip": {
            "attraction": {
                "id": booking_data[2],
                "name": attraction_data[0][0],
                "address": attraction_data[0][1],
                "image": attraction_data[0][2]
            },
            "date": str(booking_data[3]),
            "time": order_data[4]
        },
        "contact": {
            "name": order_data[3],
            "email": order_data[4],
            "phone": order_data[5]
        },
        "status": order_data[2]
    }
    return order_info
