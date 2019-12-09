import jwt
from aiohttp import web
from aiohttp.web_response import json_response

from api.db.tables import users


async def jwt_auth_middleware(app, handler):
    """ Jwt Token Middleware that takes JWT token from Authorization header
    and validate logged user

    :param app: web Application
    :param handler: function that handle input Request
    :return:
    """
    async def middleware(request: web.Request):
        request.user = None
        jwt_config = request.app['config']['jwt_auth']
        jwt_token = request.headers.get('Authorization')
        if jwt_token:
            try:
                payload = jwt.decode(
                    jwt=jwt_token,
                    key=jwt_config['jwt_secret'],
                    algorithms=[jwt_config['jwt_algorithm']]
                 )
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return json_response({'message': 'Token is invalid'}, status=400)
            async with app['db'].acquire() as connection:
                cursor = await connection.execute(
                    users.select()
                        .where(users.c.id == payload['user_id'])
                )
                user = await cursor.fetchone()
                request.user = dict(user)
        return await handler(request)
    return middleware

