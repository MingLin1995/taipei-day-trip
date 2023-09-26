from flask import *
from model.database import connection_pool_TP_data, execute_query

# 使用 Blueprint 創建路由
mrts_bp = Blueprint('mrts', __name__)

""" 取得捷運站名稱列表 """


@mrts_bp.route("/api/mrts")
def get_mrts():
    try:
        mrts = get_mrt_names(connection_pool_TP_data)
        return jsonify(mrts), 200
    except Exception:
        error_response = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(error_response), 500


def get_mrt_names(connection_pool_TP_data):
    query = """
        SELECT a.mrt 
        FROM attractions a
        GROUP BY a.mrt
        ORDER BY COUNT(*) DESC, a.mrt
    """

    result = execute_query(connection_pool_TP_data, query)

    mrts = []
    count = 0
    for row in result:
        if row[0] is not None:
            mrts.append(row[0])
            count += 1
            if count >= 40:
                break

    return {"data": mrts}
