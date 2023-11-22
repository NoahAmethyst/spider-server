import logging
import sys

import coloredlogs

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(name='spider-logger')
coloredlogs.install(logger=logger)
logger.propagate = False


def InitLogger():
    ## Setup logger color
    coloredFormatter = coloredlogs.ColoredFormatter(
        fmt='[%(name)s] %(asctime)s %(funcName)s %(lineno)-3d  %(message)s',
        level_styles=dict(
            debug=dict(color='white'),
            info=dict(color='green'),
            warning=dict(color='yellow', bright=True),
            error=dict(color='red', bold=True, bright=True),
            critical=dict(color='black', bold=True, background='red'),
        ),
        field_styles=dict(
            name=dict(color='white'),
            asctime=dict(color='white'),
            funcName=dict(color='white'),
            lineno=dict(color='white'),
        )
    )

    ## Setup logger streamHandler
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setFormatter(fmt=coloredFormatter)
    logger.addHandler(hdlr=ch)
    logger.setLevel(level=logging.DEBUG)

    ## Output example

    # logger.debug(msg="this is a debug message")
    # logger.info(msg="this is an info message")
    # logger.warning(msg="this is a warning message")
    # logger.error(msg="this is an error message")
    # logger.critical(msg="this is a critical message")
