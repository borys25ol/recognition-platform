from aiohttp.web_response import json_response


def login_required(func):
    """ Login required decorator for checking if user is auth

    :param func: Request Handler
    :return:
    """
    def wrapper(request):
        if not request.user:
            return json_response({'message': 'Auth required'}, status=401)
        return func(request)
    return wrapper
