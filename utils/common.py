import argparse
import os
from pathlib import Path
from typing import Any

import trafaret as T
from aiohttp import web
from trafaret_config import commandline

PROJECT_PATH = Path(__file__).parent.parent
DEFAULT_CONFIG_FILE = os.environ.get('CONFIG_FILE', 'dev.yml')
DEFAULT_CONFIG_PATH = PROJECT_PATH / 'config' / DEFAULT_CONFIG_FILE

TRAFARET = T.Dict({
    T.Key('app'):
        T.Dict({
            'host': T.String(),
            'port': T.Int(),
            'workers': T.Int(),
        }),
    T.Key('postgres'):
        T.Dict({
            'user': T.String(),
            'password': T.String(),
            'database': T.String(),
            'port': T.Int(),
            'host': T.String(),
        }),
    T.Key('redis'):
        T.Dict({
            'port': T.Int(),
            'host': T.String(),
        }),
    T.Key('jwt_auth'):
        T.Dict({
            'jwt_secret': T.String(),
            'jwt_algorithm': T.String(),
            'jset_exp_delta_seconds': T.Int(),
        }),
})


def get_config(argv: Any = None) -> Any:
    """
    Load settings to dict from YML-file
    :param argv:
    :return: Config dict
    """

    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        ap,
        default_config=DEFAULT_CONFIG_PATH
    )

    # ignore unknown options
    if isinstance(argv, str):
        options, unknown = ap.parse_known_args(['-c', argv])
    else:
        options, unknown = ap.parse_known_args(argv)

    config = commandline.config_from_options(options, TRAFARET)
    return config


def init_config(app: web.Application, config: str) -> None:
    """
    Initialize config file for application
    :param app: Current App object
    :param config: Path to config file
    :return:
    """
    app['config'] = get_config(config or ['-c', DEFAULT_CONFIG_PATH.as_posix()])
