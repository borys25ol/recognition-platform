import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

import aioredis
from aiohttp import web

from api.db.db import init_pg, close_pg
from utils.common import init_config
from .routes import init_routes

templates_path = os.path.join(os.path.dirname(__file__), 'templates')


async def redis(app: web.Application) -> None:
    """A function that, when the server is started, connects to redis,
    and after stopping it breaks the connection (after yield)

    :param app:
    :return:
    """
    config = app['config']['redis']

    create_redis = partial(
        aioredis.create_redis,
        f'redis://{config["host"]}:{config["port"]}'
    )
    app['create_redis'] = await create_redis()

    yield

    app['create_redis'].close()
    await app['create_redis'].wait_closed()


async def init_executor(app: web.Application) -> web.Application:
    """ Initialize ThreadPoolExecutor for running blocking tasks

    :param app: Web application
    :return: Web application
    """
    app['tasks'] = []
    app['executor'] = ThreadPoolExecutor()

    return app


async def close_executor(app: web.Application) -> web.Application:
    """ Shutdown executor instance

    :param app: Web application
    :return: Web application
    """
    for task in app['tasks']:
        task.cancel()
        await task

    app['executor'].shutdown()

    return app


def init_app(config=None) -> web.Application:
    """ Initialize application

    :param config:
    :return:
    """
    app = web.Application()

    init_config(app, config)

    # create db connection on startup, shutdown on exit
    app.on_startup.append(init_pg)
    app.on_startup.append(init_executor)

    app.on_cleanup.append(close_pg)
    app.on_cleanup.append(close_executor)

    app.cleanup_ctx.extend([
        redis,
    ])

    # setup views and routes
    init_routes(app)

    return app