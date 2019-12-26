import aiopg
import sqlalchemy
from aiohttp import web

from api.db.tables import images


async def check_exist(connection: aiopg.connection, table: sqlalchemy.table,
                      column: sqlalchemy.column, value:str) -> bool:
    """ Function that check if specific value exist in db

    :param connection: Current connection to db
    :param table: Table where the value will search
    :param column: Column where the value will search
    :param value: Value for searching
    :return: True if value exist in db, otherwise - False
    """
    result = await connection.execute(
        table.select()
            .where(table.c[column] == value)
    )
    row = await result.fetchone()
    if row:
        if dict(row).get(column, '') == value:
            return True
        else:
            return False
    else:
        return False


async def get_result_from_db(request: web.Request, limit, offset):
    """ Get processing results from DB with offset and limit

    :param request:  web request
    :param limit: Count rows from db
    :param offset: Count rows from db need to skip
    :return: List with records from db
    """
    results = []
    async with request.app['db'].acquire() as connection:
        sql_query = """
            SELECT 
                product_id, image_url, image_text 
            FROM 
                images
            WHERE user_id = {user_id}
                LIMIT {limit} OFFSET {offset};
        """.format(
            limit=limit,
            offset=offset,
            user_id=request.app['user']['id']
        )

        async for row in connection.execute(sql_query):
            results.append(dict(row))

        query = await connection.execute(
            images.select()
                .where(images.c.user_id == request.app['user']['id'])
        )
        row_count = query.rowcount

    return results, row_count
