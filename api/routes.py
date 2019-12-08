import pathlib

from aiohttp import web

from api.handlers import (
    get_urls_for_recognition, post_urls_for_recognition, delete_urls_for_recognition,
    start_processing_images,
    get_all_running_tasks_count
)

PROJECT_PATH = pathlib.Path(__file__).parent


def init_routes(app: web.Application):
    """ Initialize routs for application

    :param app:
    :return:
    """
    router = app.router

    router.add_get('/api/v1/urls', get_urls_for_recognition, name='get-urls')
    router.add_post('/api/v1/urls', post_urls_for_recognition, name='post-urls')
    router.add_delete('/api/v1/urls/{product_id}', delete_urls_for_recognition, name='delete-urls')

    router.add_get('/api/v1/urls/start_processing', start_processing_images, name='start-processing')

    router.add_get('/api/v1/tasks', get_all_running_tasks_count, name='get-tasks')
