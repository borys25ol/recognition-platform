from json import JSONDecodeError

import ujson
from aiohttp import web
from aiohttp_apispec import request_schema

from api.db.db_helpers import get_result_from_db
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
    :return: web response with 201 status code or 400 if invalid json body
    """
    redis = request.app['create_redis']
    try:
        data = await request.json()
    except JSONDecodeError:
        return web.json_response({'message': 'JSON body is not correct'}, status=400)

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
    tasks = request.app['tasks']
    redis = request.app['create_redis']
    scheduler = request.app['AIOJOBS_SCHEDULER']

    keys = await redis.keys('*:start_id*')
    for key in keys:
        image_urls = await redis.smembers(key, encoding='utf-8')
        task = scheduler.spawn(async_image_process(request, key, image_urls))
        tasks.append(task)
        await task
        await redis.delete(key)

    return web.Response()


@login_required
async def get_all_running_tasks_count(request: web.Request) -> web.Response:
    """ Get all active tasks in queue.

    :param request: web request
    :return: web response in json format
    """
    running_tasks_count = request.app['AIOJOBS_SCHEDULER'].active_count
    pending_tasks_count = request.app['AIOJOBS_SCHEDULER'].pending_count

    data = {
        'running_tasks': running_tasks_count,
        'pending_tasks': pending_tasks_count,
    }
    return web.json_response(data)


@login_required
async def get_json_result(request: web.Request) -> web.Response:
    """ Get all paginated results from tasks.

    :param request: web request
    :return: web response in json format
    """
    query = request.query

    try:
        offset = int(query.get('offset', 0))
        limit = int(query.get('limit', 24))
    except ValueError:
        return web.json_response({'message': 'Invalid query params'}, dumps=ujson.dumps)

    limit = min(limit, 24)

    data, row_count = await get_result_from_db(request, limit, offset)

    return web.json_response({'count': row_count, 'results': data}, dumps=ujson.dumps)
