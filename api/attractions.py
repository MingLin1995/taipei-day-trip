from flask import *
import json
from model.database import connection_pool_TP_data

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
    connection = connection_pool_TP_data.get_connection()
    cursor = connection.cursor(dictionary=True)

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
        cursor.execute(query, (keyword_pattern, keyword,
                       offset, items_per_page+1))
        result = cursor.fetchall()

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
        cursor.execute(query, (offset, items_per_page+1))
        result = cursor.fetchall()

    # 用多查詢一筆的方式去判斷是否還有下一頁
    next_page = None
    if len(result) > items_per_page:
        next_page = page + 1
        result = result[:items_per_page]  # 只返回前12条数据

    data = []

    for row in result:
        attraction_id = row["id"]
        images = get_attraction_images(attraction_id, cursor)
        row["images"] = images
        row["lat"] = float(row["lat"])
        row["lng"] = float(row["lng"])
        data.append(row)

    cursor.close()
    connection.close()

    return {
        "nextPage": next_page,
        "data": data
    }


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


def get_basic_attraction_info(attraction_id, cursor):
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

    cursor.execute(query, (attraction_id,))
    result = cursor.fetchone()
    return result


def get_attraction_images(attraction_id, cursor):
    # 圖片URL
    image_query = """
    SELECT
        i.image_url
    FROM
        images i
    WHERE
        i.attraction_id = %s
    """
    cursor.execute(image_query, (attraction_id,))
    image_results = cursor.fetchall()
    images = [image_result['image_url'] for image_result in image_results]
    return images


def get_attraction_data(attraction_id):
    connection = connection_pool_TP_data.get_connection()
    cursor = connection.cursor(dictionary=True)

    # 取得基本資訊
    basic_info = get_basic_attraction_info(attraction_id, cursor)

    if basic_info:
        # 取得圖片資訊
        images = get_attraction_images(attraction_id, cursor)

        # 合并结果
        basic_info["images"] = images
        basic_info["lat"] = float(basic_info["lat"])
        basic_info["lng"] = float(basic_info["lng"])

        cursor.close()
        connection.close()

        return {"data": basic_info}
    else:
        cursor.close()
        connection.close()
        return None
