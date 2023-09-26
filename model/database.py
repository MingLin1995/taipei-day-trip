import mysql.connector.pooling

# 資料庫
db_TP_data = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "TP_data",
    "pool_size": 8
}
connection_pool_TP_data = mysql.connector.pooling.MySQLConnectionPool(
    **db_TP_data)

""" ---------------------會員系統簡化資料庫溝通流程------------------------ """


def execute_query(connection_pool_TP_data, sql, parameter=None, fetch_one=False, commit=False):
    connection = connection_pool_TP_data.get_connection()
    cur = connection.cursor()

    cur.execute(sql, parameter)

    data = cur.fetchone() if fetch_one else cur.fetchall()

    if commit:
        connection.commit()

    cur.close()
    connection.close()
    return data
