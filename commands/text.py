from telegram import Update
from telegram.ext import CallbackContext

from config.logger import log_command
from utils import get_arg, try_msg


def slashear(update: Update, context: CallbackContext) -> None:
    """
    Converts a phrase into a slash-ized version
    """
    log_command(update)
    if update.message.reply_to_message:
        words = update.message.reply_to_message.text.split()
        response = "/" + words[0].lower()
        for word in words[1:]:
            response += word.capitalize()
        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=response)


def uwuspeech(update: Update, context: CallbackContext) -> None:
    """
    Converts a phrase into an uwu-ized version
    """
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    message = arg.replace('r', 'w') \
        .replace('l', 'w') \
        .replace('k', 'c') \
        .replace('p', 'pw') \
        .replace('R', 'W') \
        .replace('L', 'W') \
        .replace('K', 'C') \
        .replace('P', 'PW')

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def repetir(update: Update, context: CallbackContext) -> None:
    """
    Repeats a given message
    """
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=arg)
