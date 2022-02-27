from enum import Enum
import argparse
from ast import arguments
from distutils import text_file
import os
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext
from typing import Text
from utils import generate_acronym, get_arg, reverse_acronym, try_msg

import data
from config.logger import logger


def desiglar(update: Update, context: CallbackContext) -> None:
    """
    Turns an acronym into its corresponding phrase
    """
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    message = data.Acronyms.get(arg.lower())
    if message is None:
        message = reverse_acronym(arg)
        message += "\n<i>Para hacer una sigla real:</i> /siglar"

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def siglar(update: Update, context: CallbackContext) -> None:
    """
    Saves a phrase as an acronym
    """
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    acronym = generate_acronym(arg)

    old_acronym = data.Acronyms.set(acronym, arg)

    message = acronym
    if old_acronym is not None:
        message += f"\n<i>(Reemplaza '{old_acronym}')</i>"

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


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
