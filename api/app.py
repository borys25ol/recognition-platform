import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

import aioredis
from aiohttp import web
from aiojobs import create_scheduler

from api.db.db import init_pg, close_pg
from api.middlewares.jwt_auth import jwt_auth_middleware
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


async def init_aiojobs(app: web.Application, **kwargs) -> web.Application:
    """ Initialize aiojobs scheduler

    :param app: Web application
    :return: Web application
    """
    app['AIOJOBS_SCHEDULER'] = await create_scheduler(**kwargs)

    return app


async def close_aiojobs(app: web.Application) -> web.Application:
    """ Close aiojobs scheduler

    :param app: Web application
    :return: Web application
    """
    await app['AIOJOBS_SCHEDULER'].close()

    return app


def init_app(config=None) -> web.Application:
    """ Initialize application

    :param config:
    :return:
    """
    app = web.Application(middlewares=[jwt_auth_middleware])

    init_config(app, config)

    # create db connection on startup, shutdown on exit
    app.on_startup.append(init_pg)
    app.on_startup.append(init_executor)
    app.on_startup.append(init_aiojobs)

    app.on_cleanup.append(close_pg)
    app.on_cleanup.append(close_executor)
    app.on_cleanup.append(close_aiojobs)


    app.cleanup_ctx.extend([
        redis,
    ])

    # setup views and routes
    init_routes(app)

    return app