import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

import aiohttp
from aiohttp import web

from api.db.tables import images
from api.processing import check_image, decode_value

TEXT_FOR_CHECKING = 'Nutrition Facts'


async def load_image_content(executor: ThreadPoolExecutor, session: aiohttp.ClientSession,
                             url: str) -> tuple:
    """ Function that read content of image and run blocking sync processing of image

    :param executor: ThreadPoolExecutor for run sync code in threads
    :param loop: Event loop
    :param session: Client Session for every
    :param url: Image url
    :return: result (True if text was found on the image else False), url (Image url)
    """
    loop = asyncio.get_running_loop()
    async with session.get(url) as response:
        content = await response.read()
        result = await loop.run_in_executor(executor, check_image, content, TEXT_FOR_CHECKING)
        return result, url


async def async_image_process(request: web.Request, product_id: bytes, image_urls: list) -> None:
    """ Function that run task for each product_id and set result to storage

    :param request: Aiohttp Request instance
    :param product_id: Product id
    :param image_urls: List with images links
    :return:
    """
    executor = request.app['executor']
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        product_id = decode_value(product_id).split(':')[0]
        download_futures = [
            load_image_content(executor, session, decode_value(url))
            for url in image_urls
        ]
        for download_future in asyncio.as_completed(download_futures):
            result, url = await download_future
            if result:
                async with request.app['db'].acquire() as connection:
                    await connection.execute(
                        images.insert().values(
                            product_id=product_id,
                            image_url=url
                        )
                    )
