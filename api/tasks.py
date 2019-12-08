import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

import aiohttp

from api.db.tables import images
from api.processing import check_image, decode_value

TEXT_FOR_CHECKING = 'Nutrition Facts'


async def load_image_content(executor: ThreadPoolExecutor, loop: asyncio.AbstractEventLoop,
                             session: aiohttp.ClientSession, url: str) -> tuple:
    """ Function that read content of image and run blocking sync processing of image

    :param executor: ThreadPoolExecutor for run sync code in threads
    :param loop: Event loop
    :param session: Client Session for every
    :param url: Image url
    :return: result (True if text was found on the image else False), url (Image url)
    """
    async with session.get(url) as response:
        content = await response.read()
        result = await loop.run_in_executor(executor, check_image, content, TEXT_FOR_CHECKING)
        return result, url


async def async_image_process(loop: asyncio.AbstractEventLoop, executor: ThreadPoolExecutor,
                              redis, data: dict) -> None:
    """ Function that run task for each product_id and set result to storage

    :param loop: Event loop
    :param executor: ThreadPoolExecutor for run sync code in threads
    :param redis: current Redis object for setting results
    :param data: Dict with product_id as a key and list of images as value
    :return:
    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        product_id = list(data.keys())[0]
        download_futures = [
            load_image_content(executor, loop, session, decode_value(url))
            for url in list(data.values())[0]
        ]
        for download_future in asyncio.as_completed(download_futures):
            result, url = await download_future
            if result:
                await redis.set('{}:result'.format(decode_value(product_id)), url)
            else:
                await redis.set('{}:result'.format(decode_value(product_id)), '')


async def _load_data_to_postgres(request):
    """ Callback function that setting all results from Redis to Postgres after all task done

    :param request: web Request instance
    :return:
    """
    redis = request.app['create_redis']
    keys = await redis.keys('*:result*')
    for key in keys:
        product_id = decode_value(key).split(':')[0]
        image_url = decode_value(await redis.get(key))
        async with request.app['db'].acquire() as connection:
            cursor = await connection.execute(
                images.select()
                    .where(images.c.product_id == product_id)
            )
            record = await cursor.fetchone()
            if not record:
                await connection.execute(
                    images.insert().values(
                        product_id=product_id,
                        image_url=image_url
                    )
                )


def load_data_callback(request, loop):
    loop.create_task(_load_data_to_postgres(request))
