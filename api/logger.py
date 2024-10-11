import logging
import sys


def logger_factory():
    logger = logging.getLogger("uvicorn.info")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # To print log messages in python sessions, e.g. ipython
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    logger.propagate = False

    return logger


logger = logger_factory()
