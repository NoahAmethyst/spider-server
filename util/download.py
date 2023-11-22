import logging

import requests

from util.logger import logger


def download_image(url, filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filename, 'wb') as out_file:
        out_file.write(response.content)
    logger.info(f'file successfully downloaded:{filename}')
