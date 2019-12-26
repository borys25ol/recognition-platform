import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

import aiohttp
from aiohttp import web

from api.db.db_helpers import check_exist
from api.db.tables import images
from api.processing import check_image, decode_value
from utils.logging import create_logger

logger = create_logger(__name__)


async def load_image_content(executor: ThreadPoolExecutor, session: aiohttp.ClientSession,
                             image_urls: list, image_text: str) -> tuple:
    """ Function that read content of image and run blocking sync processing of image

    :param executor: ThreadPoolExecutor for run sync code in threads
    :param session: Client Session for every
    :param image_urls: List with image urls
    :param image_text: Text for checking on image
    :return: result (True if text was found on the image else False), url (Image url)
    """
    loop = asyncio.get_running_loop()
    for url in image_urls:
        async with session.get(url) as response:
            content = await response.read()
            result = await loop.run_in_executor(executor, check_image, content, image_text)
            if result:
                return result, url


async def async_image_process(request: web.Request, product_id: bytes, image_urls: list,
                              image_text: str) -> None:
    """ Function that run task for each product_id and set result to storage

    :param request: Aiohttp Request instance
    :param product_id: Product id
    :param image_urls: List with images links
    :param image_text: Text for checking on image
    :return:
    """
    executor = request.app['executor']
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        product_id = decode_value(product_id).split(':')[0]
        data = await load_image_content(executor, session, image_urls, image_text)

        logger.info('Received result from id: {id}'.format(id=product_id))

        if data:
            result, url = data
        else:
            result, url = None, None

        async with request.app['db'].acquire() as connection:
            value_exist = await check_exist(connection, images, 'product_id', product_id)
            if not value_exist:
                if result:
                    await connection.execute(
                        images.insert().values(
                            product_id=product_id,
                            image_url=url,
                            user_id=request.app['user']['id'],
                            image_text=image_text
                        )
                    )
                    logger.info('Successfully pushed to DB data with ID: {id}, URL: {url}'.format(
                        id=product_id, url=url))

                else:
                    await connection.execute(
                        images.insert().values(
                            product_id=product_id,
                            image_url='n/a',
                            user_id=request.app['user']['id'],
                            image_text=image_text
                        )
                    )
                    logger.info('Text on images not found. Pushed empty data with ID: {id}'.format(
                        id=product_id))
            else:
                logger.info('Record with ID: {id} already exist in DB'.format(
                    id=product_id))
