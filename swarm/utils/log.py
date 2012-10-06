"Setup global logger object, including log rotating"

import logging
import sys
from logging.handlers import RotatingFileHandler

from tornado.options import options


def getLogger():

    log_file = getattr(options, 'log_file', None)
    debug = getattr(options, 'debug', False)
    if log_file:
        handler = RotatingFileHandler(log_file,
                                      maxBytes=10000000,
                                      backupCount=5)
    else:
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s:%(lineno)-4d %(message)s"
        )

    handler.setFormatter(formatter)

    logger = logging.getLogger()

    if logger.handlers:
        for i in range(len(logger.handlers)):
            logger.removeHandler(logger.handlers[i])

    logger.addHandler(handler)
    
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger


log = getLogger()


def init_logging():
    global log
    log = getLogger()
    log.info("Logging is initalized")
    log.debug("in DEBUG mode")
