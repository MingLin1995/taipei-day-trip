from flask import *
import json
from model.database import execute_query

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


# 取得景點資料(頁數搜尋以及關鍵字搜尋)


def get_attractions_data(page, keyword):
    items_per_page = 12  # 一次顯示12筆
    offset = page * items_per_page  # 從第幾項開始顯示

    if keyword:  # 關鍵字搜尋
        query = """
            SELECT
                a.id,
                a.name,
                a.category,
                a.description,
                a.address,
                a.transport,
                a.mrt,
                a.lat,
                a.lng,
                GROUP_CONCAT(i.image_url) AS images
            FROM
                attractions a
            JOIN
                images i ON a.id = i.attraction_id
            WHERE
                a.name LIKE %s OR a.mrt = %s
            GROUP BY
                a.id
            LIMIT %s, %s
        """
        keyword_pattern = f"%{keyword}%"
        parameter = (keyword_pattern, keyword, offset, items_per_page + 1)
    else:  # 頁數搜尋
        query = """
            SELECT
                a.id,
                a.name,
                a.category,
                a.description,
                a.address,
                a.transport,
                a.mrt,
                a.lat,
                a.lng,
                GROUP_CONCAT(i.image_url) AS images
            FROM
                attractions a
            JOIN
                images i ON a.id = i.attraction_id
            GROUP BY
                a.id
            LIMIT %s, %s
        """
        parameter = (offset, items_per_page + 1)

    result = execute_query(query, parameter)

    # 用多查詢一筆的方式去判斷是否還有下一頁
    next_page = None
    if len(result) > items_per_page:
        next_page = page + 1
        result = result[:items_per_page]  # 只取前12筆資料

    data = []

    for row in result:
        # 將元組轉換為列表，以便修改資料
        row_list = list(row)
        attraction_id = row_list[0]
        images = get_attraction_images(attraction_id)
        row_list[9] = images
        row_list[7] = float(row_list[7])
        row_list[8] = float(row_list[8])

        # 將修改後的列表轉換為字典形式
        formatted_row = {
            "id": row_list[0],
            "name": row_list[1],
            "category": row_list[2],
            "description": row_list[3],
            "address": row_list[4],
            "transport": row_list[5],
            "mrt": row_list[6],
            "lat": row_list[7],
            "lng": row_list[8],
            "images": row_list[9]
        }
        data.append(formatted_row)

    response_data = {
        "nextPage": next_page,
        "data": data
    }

    return response_data


def get_attraction_images(attraction_id):
    image_query = """
    SELECT
        i.image_url
    FROM
        images i
    WHERE
        i.attraction_id = %s
    """
    parameter = (attraction_id,)

    image_results = execute_query(
        image_query, parameter)
    images = [image_result[0] for image_result in image_results]
    return images


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


def get_attraction_data(attraction_id):
    # 取得基本資訊
    basic_info = get_basic_attraction_info(
        attraction_id)

    if basic_info:
        # 將基本資訊轉換成 JSON 格式
        formatted_info = {
            "data": {
                "id": basic_info[0],
                "name": basic_info[1],
                "category": basic_info[2],
                "description": basic_info[3],
                "address": basic_info[4],
                "transport": basic_info[5],
                "mrt": basic_info[6],
                "lat": float(basic_info[7]),
                "lng": float(basic_info[8]),
                "images": []
            }
        }

        # 取得圖片資訊
        images = get_attraction_images(basic_info[0])

        # 將圖片資訊添加到 formatted_info 中
        formatted_info["data"]["images"] = images

        return formatted_info
    else:
        return None


def get_basic_attraction_info(attraction_id):
    # 取得基本資訊
    query = """
        SELECT
            a.id,
            a.name,
            a.category,
            a.description,
            a.address,
            a.transport,
            a.mrt,
            a.lat,
            a.lng
        FROM
            attractions a
        WHERE
            a.id = %s
    """
    parameter = (attraction_id,)
    result = execute_query(
        query, parameter, fetch_one=True)
    return result
