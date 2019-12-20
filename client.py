import os
import asyncio
import csv
from pathlib import Path

import aiohttp
from aiohttp import TCPConnector
from dotenv import load_dotenv

from utils.logging import create_logger

ENV_PATH = Path('.') / '.env'
load_dotenv(dotenv_path=ENV_PATH)

BASE = 'http://0.0.0.0:7000'
CREATE_TASK_ENDPOINT = '{}/api/v1/urls'.format(BASE)
LOGIN_ENDPOINT = '{}/api/v1/login'.format(BASE)
HEADERS = {'Content-Type': 'application/json'}
CSV_PATH = os.getenv("CSV_PATH")
CREDENTIALS = {'email': os.getenv("EMAIL"), 'password': os.getenv("PASSWORD")}

logger = create_logger(__name__)


def get_csv_data(csv_path: str) -> list:
    """ Open and read CSV file and return list of dicts with data.

    :param csv_path: Path to CSV file
    :return: List with rows of CSV file
    """
    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)
        data = [dict(row) for row in reader]
        return data


def create_tasks(data: list) -> list:
    """ Function that created list with tasks.
    Task is a dict with 2 fields:
    1. product_id -> ID or UPC-code of product on website
    2. images_urls -> list of all images from product on website

    :param data: List with rows of CSV file
    :return: List of tasks
    """
    tasks = []
    for row in data:
        task_id = row['upc'].replace('"', '')
        images_urls = row['pictures'].split(', ')
        tasks.append(dict(product_id=task_id, images_urls=images_urls))
    return tasks


async def get_auth_token(session: aiohttp.ClientSession):
    """ Function that login user and return JWT-token.

    :param session: Current client request session
    :return: JWT-token
    """
    async with session.post(LOGIN_ENDPOINT, json=CREDENTIALS) as response:
        logger.info('Start getting token...')
        data = await response.json()
        token = data.get('token')
        if not token:
            logger.info('Auth error')
        logger.info('Token receive successfully')
        return token


async def push_task(session: aiohttp.ClientSession, task: dict) -> None:
    """ Function that create push task in queue on server.

    :param session: Current client request session
    :param task: dict with product_id and images_urls
    :return:
    """
    if not HEADERS.get('Authorization'):
        auth_token = await get_auth_token(session)
        HEADERS['Authorization'] = auth_token
    async with session.post(CREATE_TASK_ENDPOINT, json=task, headers=HEADERS) as response:
        if response.status == 201:
            logger.info('Task {} created successfully'.format(task['product_id']))
        else:
            logger.info('Task {} throw some error'.format(task['product_id']))


async def main(tasks: list):
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        for task in tasks:
            await push_task(session, task)


if __name__ == '__main__':
    csv_data = get_csv_data(CSV_PATH)
    tasks = create_tasks(csv_data)
    asyncio.run(main(tasks))
