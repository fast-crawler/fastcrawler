import logging

from fastcrawler import Logger

logger = Logger(level=logging.INFO)
logger.error("msg")
logger.info("msg")
logger.debug("msg")
logger.warning("msg")
print(logger.repo.filter_by().all())
