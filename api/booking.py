from flask import *
from model.JWT import validate_token
from model.booking import create_booking, find_booking_inf
from model.booking import update_booking_status


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
