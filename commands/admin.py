import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import member_exclusive
from config.logger import log_command


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
