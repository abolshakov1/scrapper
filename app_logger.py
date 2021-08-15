import logging
from logging.config import fileConfig

fileConfig('logging.cfg')

logger = logging.getLogger()
bot_sender_logger = logging.getLogger('bot_sender')
telegram_worker_logger = logging.getLogger('telegram_worker')
scrapper_logger = logging.getLogger('scrapper')
