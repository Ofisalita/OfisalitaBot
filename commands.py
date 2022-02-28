import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext
from typing import Text
from utils import generate_acronym, get_arg, reverse_acronym, try_msg

import data
from config.logger import log_command
from utils import generate_acronym, get_arg, try_msg


def start(update: Update, context: CallbackContext) -> None:
    """
    Send a message when the command /start is issued.
    """
    log_command(update)
    message = "ola ceamos hamigos"
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)

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
