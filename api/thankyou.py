from flask import *
from model.JWT import validate_token
from model.database import connection_pool_TP_data,  execute_query


# 使用 Blueprint 創建路由
thankyou_bp = Blueprint('thankyou', __name__)

""" 取得付款資訊 """


@thankyou_bp.route('/api/order/<int:orderNumber>', methods=['GET'])
def get_booking_inf(orderNumber):
    try:
        token_data = validate_token()
        if token_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        # 查詢orders資訊
        sql = "SELECT * FROM orders WHERE number = %s"
        order_data = execute_query(
            connection_pool_TP_data, sql, (str(orderNumber),), fetch_one=True)

        if order_data is None:
            return jsonify({"data": None}), 404

        # 查詢booking資訊
        sql = "SELECT * FROM booking WHERE member_id = %s"
        booking_data = execute_query(
            connection_pool_TP_data, sql, (order_data[6],), fetch_one=True)

        # 查詢景點資訊
        sql = """
            SELECT a.name, a.address, i.image_url
            FROM attractions AS a
            LEFT JOIN images AS i ON a.id = i.attraction_id
            WHERE a.id = %s
        """
        attraction_data = execute_query(
            connection_pool_TP_data, sql, (booking_data[2],))

        new_order_info = {
            "number": str(orderNumber),
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

        response_data = {
            "data": new_order_info
        }

        return jsonify(response_data), 200
    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
