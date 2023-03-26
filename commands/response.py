from telegram import Update
from telegram.ext import CallbackContext

from config.logger import log_command
from utils import try_msg, try_sticker


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


def tup(update: Update, context: CallbackContext) -> None:
    """
    Responds with the message 'tup'
    """
    log_command(update)
    message = "tup"
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def gracias(update: Update, context: CallbackContext) -> None:
    """
    Responds with a sticker saying "you're welcome!"
    """
    log_command(update)

    try_sticker(context.bot,
                chat_id=update.message.chat_id,
                sticker="CAACAgEAAxkBAAEIGOFkDPttpRc6CvU2knm"
                        "-GXAwP8inxgAC3AEAAqnzSUfg84mzRL-JRS8E")
