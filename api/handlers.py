import asyncio

import ujson
from aiohttp import web
from aiohttp_apispec import request_schema

from api.tasks import async_image_process, load_data_callback
from api.schemas import UrlsDataSchema, ProductIdSchema


async def get_urls_for_recognition(request: web.Request) -> web.Response:
    """ Get all images urls from Redis.

    :param request: web request
    :return: web response in json format
    """
    redis = request.app['create_redis']

    response_data = await redis.keys('*')

    return web.json_response({"ids": response_data}, dumps=ujson.dumps)


@request_schema(UrlsDataSchema)
async def post_urls_for_recognition(request: web.Request) -> web.Response:
    """ Set all images to Redis.

    :param request: web request
    :return: web response with 201 status code
    """
    redis = request.app['create_redis']
    data = await request.json()

    await redis.sadd(data['product_id'], *data['images_urls'])

    return web.HTTPCreated()


@request_schema(ProductIdSchema)
async def delete_urls_for_recognition(request: web.Request) -> web.Response:
    """ Delete images urls from Redis by product id.

    :param request: web request
    :return: web response with 204 status code
    """
    redis = request.app['create_redis']
    product_id = request.match_info['product_id']

    await redis.delete(product_id)

    return web.HTTPNoContent()


async def start_processing_images(request: web.Request) -> web.Response:
    """ Start processing images

    :param request: web request
    :return:
    """
    executor = request.app['executor']
    redis = request.app['create_redis']
    loop = asyncio.get_event_loop()

    keys = await redis.keys('*')
    for key in keys:
        if 'result' not in key.decode('utf-8'):
            image_urls = await redis.smembers(key)
            data = {key: image_urls}
            task = asyncio.create_task(
                async_image_process(loop, executor, redis, data)
            )
            task.add_done_callback(lambda t: load_data_callback(request, loop))

    return web.Response()


async def get_all_running_tasks_count(request: web.Request) -> web.Response:
    """ Get all active tasks in queue.

    :param request: web request
    :return: web response in json format
    """
    all_tasks_count = len(asyncio.Task.all_tasks())

    return web.json_response({'tasks_count': all_tasks_count - 5})