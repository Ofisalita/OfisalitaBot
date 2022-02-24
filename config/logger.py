import logging
from logging.handlers import RotatingFileHandler
from os import path

# 3 MB max files, up to 2 backup files.
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s - [%(funcName)s:%(lineno)d]',
                    level=logging.INFO,
                    handlers=[RotatingFileHandler(path.relpath('log/bot.log'), mode='a', maxBytes=3*1024*1024,
                                                  backupCount=2, encoding=None, delay=0)])

logger = logging.getLogger('pasoapasobot')

def log_command(update):
    logger.info(f"[Command '{update.message.text}' from {update.message.chat_id}]")