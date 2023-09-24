from flask import *
from model.database import connection_pool_TP_data

# 使用 Blueprint 創建路由
mrts_bp = Blueprint('mrts', __name__)

""" 取得捷運站名稱列表 """


@mrts_bp.route("/api/mrts")
def get_mrts():
    try:
        mrts = get_mrt_names()
        return jsonify(mrts), 200
    except Exception:
        error_response = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(error_response), 500


def get_mrt_names():
    connection = connection_pool_TP_data.get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT a.mrt 
        FROM attractions a
        GROUP BY a.mrt
        ORDER BY COUNT(*) DESC, a.mrt
    """

    cursor.execute(query)
    result = cursor.fetchall()

    mrts = []
    count = 0
    for row in result:
        if row["mrt"] is not None:
            mrts.append(row["mrt"])
            count += 1
            if count >= 40:
                break

    cursor.close()
    connection.close()

    return {"data": mrts}
