import random

try:
    from PIL import Image
except ImportError:
    import Image
from io import BytesIO

import pytesseract


def check_image(body, text):
    """ Function that read image body and check text on image
    :param body: Image bytes body
    :param text: Text that need to check on image
    :return:
    """
    image = Image.open(BytesIO(body))
    picture_data = pytesseract.image_to_string(image)

    if text in picture_data:
        return True
    return False


def decode_value(value):
    """ Function that decoded value to utf-8
    :param value: bytes value
    :return:
    """
    return value.decode('utf-8')
