import logging


def create_logger(logger_name):
    """ Initialize logger

    :param logger_name:
    :return:
    """
    logger = logging.getLogger(logger_name)

    logging.basicConfig(format='[%(asctime)s]: %(message)s')
    logger.setLevel(level=logging.INFO)

    return logger