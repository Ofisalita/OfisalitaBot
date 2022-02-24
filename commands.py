import os
from datetime import datetime
from utils import try_msg

from config.logger import log_command


def start(update, context):
    log_command(update)
    message = "ola ceamos hamigos"
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def tup(update, context):
    log_command(update)
    message = "tup"
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)

# Admin Commands

def get_log(update, context):
    log_command(update)
    context.bot.send_document(chat_id=update.message.from_user.id,
                              document=open(os.path.relpath('log/bot.log'), 'rb'),
                              filename=f"pasoapasobot_log_{datetime.now().strftime('%d%b%Y-%H%M%S')}.txt")
