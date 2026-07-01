import logging
import sys
from loguru import logger
from app.settings import settings


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2

        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_log():
    logger.remove()
    format_log = '<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>'
    log_file = f'{settings.BASEDIR}/{settings.LOGFILE}'
    level = 10 if settings.DEBUG else 20
    logger.add(sys.stdout, colorize=True, format=format_log)
    logger.add(log_file, format=format_log, rotation='1 MB', retention=3, compression='zip')
    logging.basicConfig(handlers=[InterceptHandler()], level=level, force=True)
    logging.getLogger('telethon').setLevel(level)
