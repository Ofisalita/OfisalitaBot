from enum import Enum

from config.logger import logger


def log_command(update):
    logger.info((
        f"[Command '{update.message.text}' "
        f"from {update.message.chat_id}]"
    ))


class Commands(str, Enum):
    TUP = "tup"
    START = "start"
    DESIGLAR = "desiglar"
    SIGLAR = "siglar"
    SLASHEAR = "slashear"
    UWUSPEECH = "uwuspeech"
    GET_LOG = "get_log"
