import logging

from pb.spider_pb2 import Message
from util.logger import logger

def recv_message(msg: Message):
    logger.info(f'recv message:{msg}')





