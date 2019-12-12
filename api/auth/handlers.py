import datetime
from datetime import timedelta

import jwt
from aiohttp import web
from aiohttp.web_response import json_response
from aiohttp_apispec import request_schema
import trafaret as T
from trafaret import DataError
from werkzeug.security import generate_password_hash, check_password_hash

from api.db.tables import users
from api.schemas import UserLoginSchema, UserRegisterSchema
from api.validators.auth import LOGIN_TRAFARET, REGISTER_TRAFARET


@request_schema(UserLoginSchema)
async def login_user(request: web.Request) -> web.Response:
    """ Login user handler. Check if user exist in database and generate JWT token

    :param request: web request
    :return: web response in json format
    """
    jwt_config = request.app['config']['jwt_auth']
    json_data = await request.json()

    result = T.catch_error(LOGIN_TRAFARET, json_data)
    if isinstance(result, DataError):
        errors = result.as_dict()
        return json_response({'errors': errors}, status=400)

    async with request.app['db'].acquire() as connection:
        cursor = await connection.execute(
            users.select()
                .where(users.c.email == json_data['email'])
        )
        user_credentials = await cursor.fetchone()
        if not user_credentials:
            return json_response({
                'message': 'User with email {email} does not exist'.format(email=json_data['email'])
            }, status=403)
        else:
            id, email, password = user_credentials['id'], user_credentials['email'], user_credentials['password']
            if check_password_hash(password, json_data['password']):
                payload = {
                    'user_id': id,
                    'user_email': email,
                    'exp': datetime.datetime.utcnow() + timedelta(seconds=jwt_config['jset_exp_delta_seconds'])
                }
                jwt_token = jwt.encode(payload, jwt_config['jwt_secret'], jwt_config['jwt_algorithm'])
                return json_response({'token': jwt_token.decode('utf-8')})
            else:
                return json_response({'message': 'Password is not correct'}, status=401)


@request_schema(UserRegisterSchema)
async def register_user(request: web.Request) -> web.Response:
    """ Register user handler. Check if user already exist or create new user in database

    :param request: web request
    :return: web response in json format
    """
    json_data = await request.json()
    result = T.catch_error(REGISTER_TRAFARET, json_data)
    if isinstance(result, DataError):
        errors = result.as_dict()
        return json_response({'errors': errors}, status=400)

    async with request.app['db'].acquire() as connection:
        cursor = await connection.execute(
            users.select()
                .where(users.c.email == json_data['email'])
        )
        user_credentials = await cursor.fetchone()
        if user_credentials:
            return json_response({
                'message': 'User with email {email} already exist'.format(email=json_data['email'])
            })
        else:
            await connection.execute(
                users.insert().values(
                    name=json_data['name'],
                    last_name=json_data['last_name'],
                    email=json_data['email'],
                    password=generate_password_hash(json_data['password']),
                )
            )
            return json_response({
                'message': 'User with email {email} register successfully'.format(email=json_data['email'])
            })
