import asyncio
import logging
import os
import sys
import threading

from job import run_schedule
from server import server

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    addr = os.environ.get('GRPC_SERVER')
    thread = threading.Thread(target=run_schedule)
    thread.start()

    asyncio.run(server.start(addr))
