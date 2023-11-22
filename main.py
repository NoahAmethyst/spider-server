import asyncio
import logging
import os
import sys
import threading

import coloredlogs

from job import run_schedule
from server import server
from util.logger import InitLogger

if __name__ == '__main__':
    InitLogger()

    addr = os.environ.get('GRPC_SERVER')
    thread = threading.Thread(target=run_schedule)
    thread.start()

    asyncio.run(server.start(addr))
