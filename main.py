import argparse
import asyncio

from aiohttp import web

from api.app import init_app

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    print('Library uvloop is not available')

parser = argparse.ArgumentParser(description="Text api project")
parser.add_argument('--reload', action='store_true', help='Auto reload code on changes')
parser.add_argument('-c', "--config", help='Path to config file')

args = parser.parse_args()

if args.reload:
    print('Start with code reloading')
    import aioreloader

    aioreloader.start()


def main():
    """
    Entry point for project. Run application on host and port from config
    :return:
    """
    app = init_app(args.config)
    config = app['config']['app']

    web.run_app(
        app,
        host=config['host'],
        port=config['port']
    )


if __name__ == '__main__':
    main()