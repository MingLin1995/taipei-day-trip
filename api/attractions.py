from flask import *
import json
from model.attractions import get_attractions_data, get_attraction_data
# 使用 Blueprint 創建路由
attractions_bp = Blueprint('attractions', __name__)

""" 取得景點資料列表 """


@attractions_bp.route("/api/attractions")
def attractions_data():
    page = int(request.args.get("page", 0))  # 預設0，整數格式
    keyword = request.args.get("keyword", "")
    try:
        data = get_attractions_data(page, keyword)
        # 回傳資料不要透過jsonify，排序會亂
        json_data = json.dumps(data)
        response = Response(
            json_data, content_type="application/json", status=200)
        return response
    except Exception:
        response = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(response), 500


""" 根據景點編號取得景點資料 """


@attractions_bp.route("/api/attractions/<int:attractionId>")
def get_attraction(attractionId):
    try:
        attraction = get_attraction_data(attractionId)
        if attraction is not None:
            json_data = json.dumps(attraction)
            response = Response(
                json_data, content_type="application/json", status=200)
            return response
        else:
            error_response = {
                "error": True,
                "message": "景點編號不正確"
            }
            return jsonify(error_response), 400
    except Exception:
        error_response = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(error_response), 500
