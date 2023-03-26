import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import member_exclusive
from config.logger import log_command
from utils import try_delete, guard_reply_to_message, \
    guard_reply_to_bot_message


@member_exclusive
def get_log(update: Update, context: CallbackContext) -> None:
    """
    Gets the bot's command log
    """
    log_command(update)
    context.bot.send_document(chat_id=update.message.from_user.id,
                              document=open(os.path.relpath(
                                  'log/bot.log'), 'rb'),
                              filename=(
                                  "pasoapasobot_log_"
                                  f"{datetime.now().strftime('%d%b%Y-%H%M%S')}"
                                  ".txt"
                              ))


@member_exclusive
def prohibir(update: Update, context: CallbackContext) -> None:
    """
    Deletes the message being replied to if it was sent by the bot
    """
    log_command(update)

    if guard_reply_to_message(update):
        return

    if guard_reply_to_bot_message(update, context):
        return

    try_delete(context.bot, chat_id=update.message.chat_id,
               message_id=update.message.reply_to_message.message_id)
