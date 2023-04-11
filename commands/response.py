from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import member_exclusive
from config.logger import log_command
from utils import try_msg, try_sticker, try_poll


@member_exclusive
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


@member_exclusive
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


@member_exclusive
def gracias(update: Update, context: CallbackContext) -> None:
    """
    Responds with a sticker saying "you're welcome!"
    """
    log_command(update)

    try_sticker(context.bot,
                chat_id=update.message.chat_id,
                sticker="CAACAgEAAxkBAAEIGOFkDPttpRc6CvU2knm"
                        "-GXAwP8inxgAC3AEAAqnzSUfg84mzRL-JRS8E")


@member_exclusive
def weekly_poll(update: Update, context: CallbackContext) -> None:
    """
    Sends a poll asking what days of the week people can attend
    """

    log_command(update)

    try_poll(context.bot,
             chat_id=update.message.chat_id,
             question="Esta semana voy a la U los días",
             options=["Lunes", "Martes", "Miércoles",
                      "Jueves", "Viernes", "Sábado",
                      "Domingo", "No voy / Ver respuestas"],
             is_anonymous=False,
             allows_multiple_answers=True,
             type="regular")


@member_exclusive
def reply_hello(update: Update, context: CallbackContext) -> None:
    """
    Replys with the message 'hello there'
    """
    log_command(update)
    message = "hello there"
    reply_message_id = update.message.message_id
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message,
            reply_to_message_id=reply_message_id)
