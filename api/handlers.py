import asyncio

import ujson
from aiohttp import web
from aiohttp_apispec import request_schema

from api.schemas import UrlsDataSchema, ProductIdSchema
from api.tasks import async_image_process
from utils.security import login_required


@login_required
async def get_urls_for_recognition(request: web.Request) -> web.Response:
    """ Get all images urls from Redis.

    :param request: web request
    :return: web response in json format
    """
    redis = request.app['create_redis']

    response_data = await redis.keys('*:start_id*')

    return web.json_response({"ids": response_data}, dumps=ujson.dumps)


@login_required
@request_schema(UrlsDataSchema)
async def post_urls_for_recognition(request: web.Request) -> web.Response:
    """ Set all images to Redis.

    :param request: web request
    :return: web response with 201 status code
    """
    redis = request.app['create_redis']
    data = await request.json()

    await redis.sadd('{}:start_id'.format(str(data['product_id'])), *data['images_urls'])

    return web.HTTPCreated()


@login_required
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


@login_required
async def start_processing_images(request: web.Request) -> web.Response:
    """ Start processing images

    :param request: web request
    :return:
    """
    loop = asyncio.get_running_loop()
    redis = request.app['create_redis']

    keys = await redis.keys('*:start_id*')
    for key in keys:
        image_urls = await redis.smembers(key)
        loop.create_task(
            async_image_process(request, key, image_urls)
        )
        await redis.delete(key)

    return web.Response()


@login_required
async def get_all_running_tasks_count(request: web.Request) -> web.Response:
    """ Get all active tasks in queue.

    :param request: web request
    :return: web response in json format
    """
    all_tasks_count = len(asyncio.Task.all_tasks())
    return web.json_response({'tasks_count': all_tasks_count - 6})
