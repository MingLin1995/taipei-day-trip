from flask import *
from model.JWT import validate_token
from decouple import config  # pip install python-decouple 讀取.env
from model.order import create_order, process_payment, get_order_info, get_booking_info, get_attraction_info, build_order_info
from api.booking import update_booking_status


# 使用 Blueprint 創建路由
order_bp = Blueprint('order', __name__)

""" 訂單付款 """


@order_bp.route('/api/orders', methods=['POST'])
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
            if payment_info and "error" not in payment_info:
                response_data = {
                    "data": payment_info
                }
                return jsonify(response_data), 200
            else:
                return jsonify(payment_info), 400
        else:
            return jsonify({"error": True, "message": "建立失敗，資料輸入不正確"}), 400
    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500


# 將config傳送到前端
@order_bp.route('/api/config', methods=['GET'])
def get_config():
    APP_ID = config("APP_ID")
    APP_KEY = config("APP_KEY")
    config_data = {
        "APP_ID": APP_ID,
        "APP_KEY": APP_KEY
    }
    return jsonify(config_data)


""" 取得預訂、訂單資訊 """


@order_bp.route('/api/order/<int:orderNumber>', methods=['GET'])
def get_booking_inf(orderNumber):
    try:
        token_data = validate_token()
        member_id = token_data.get("id")

        if token_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        # 查詢orders資訊
        order_data = get_order_info(orderNumber)

        if order_data is None:
            return jsonify({"data": None}), 404

        # 查詢booking資訊
        booking_data = get_booking_info(order_data[6])

        # 查詢景點資訊
        attraction_data = get_attraction_info(booking_data[2])

        # 建立新的訂單資訊
        new_order_info = build_order_info(
            orderNumber, booking_data, attraction_data, order_data)

        response_data = {
            "data": new_order_info
        }

        # 更新訂單狀態
        update_booking_status(member_id)

        return jsonify(response_data), 200
    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
