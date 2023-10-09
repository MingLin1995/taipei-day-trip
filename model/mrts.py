from model.database import execute_query


def get_mrt_names():
    query = """
        SELECT a.mrt 
        FROM attractions a
        GROUP BY a.mrt
        ORDER BY COUNT(*) DESC, a.mrt
    """

    result = execute_query(query)

    mrts = []
    count = 0
    for row in result:
        if row[0] is not None:
            mrts.append(row[0])
            count += 1
            if count >= 40:
                break

    return {"data": mrts}
