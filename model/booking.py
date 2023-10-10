from model.database import execute_query


""" 新增訂單 """


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
        existing_booking_sql, existing_booking_params, fetch_one=True)

    if existing_booking:
        # 存在的話先刪除
        delete_booking_sql = "DELETE FROM booking WHERE id = %s"
        delete_booking_params = (existing_booking[0],)
        execute_query(delete_booking_sql,
                      delete_booking_params, commit=True)
        reset_id = "ALTER TABLE booking AUTO_INCREMENT = 1"
        execute_query(reset_id, commit=True)

    # 新增訂單
    sql = "INSERT INTO booking (member_id, attractionId, date, time, price) VALUES (%s, %s, %s, %s, %s)"
    values = (member_id, attractionId, date, time, price)
    execute_query(sql, values, commit=True)

    return True


""" 取得訂單資料 """


def find_booking_inf(token_data):
    member_id = token_data.get("id")

    # 搜尋訂單資料
    sql = """
        SELECT b.date, b.time, b.price, a.id, a.name, a.address, i.image_url
        FROM booking b
        JOIN attractions a ON b.attractionId = a.id
        LEFT JOIN images i ON b.attractionId = i.attraction_id
        WHERE b.member_id = %s AND b.status = 1
    """

    result = execute_query(sql, (member_id,))

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


""" 更新訂單狀態 """


def update_booking_status(member_id):
    sql_update = "UPDATE booking SET status = 0 WHERE member_id = %s"
    update_params = (member_id,)
    execute_query(sql_update,
                  update_params, commit=True)
