from flask import *
from model.mrts import get_mrt_names

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
