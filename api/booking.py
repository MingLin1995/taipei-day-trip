from flask import *
from model.JWT import validate_token
from model.database import connection_pool_TP_data,  execute_query


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
        connection_pool_TP_data, existing_booking_sql, existing_booking_params, fetch_one=True)

    if existing_booking:
        # 存在的話先刪除
        delete_booking_sql = "DELETE FROM booking WHERE id = %s"
        delete_booking_params = (existing_booking[0],)
        execute_query(connection_pool_TP_data, delete_booking_sql,
                      delete_booking_params, commit=True)
        reset_id = "ALTER TABLE booking AUTO_INCREMENT = 1"
        execute_query(connection_pool_TP_data, reset_id, commit=True)

    # 新增訂單
    sql = "INSERT INTO booking (member_id, attractionId, date, time, price) VALUES (%s, %s, %s, %s, %s)"
    values = (member_id, attractionId, date, time, price)
    execute_query(connection_pool_TP_data, sql, values, commit=True)

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
        WHERE b.member_id = %s
    """
    result = execute_query(connection_pool_TP_data, sql, (member_id,))

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
        if token_data is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
        booking_inf = del_booking_inf(token_data)
        return jsonify(booking_inf), 200
    except Exception:
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500


def del_booking_inf(token_data):
    member_id = token_data.get("id")
    delete_booking_sql = "DELETE FROM booking WHERE member_id = %s"
    delete_booking_params = (member_id,)
    execute_query(connection_pool_TP_data, delete_booking_sql,
                  delete_booking_params, commit=True)
    reset_id = "ALTER TABLE booking AUTO_INCREMENT = 1"
    execute_query(connection_pool_TP_data, reset_id, commit=True)
