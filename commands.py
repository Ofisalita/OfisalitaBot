import os
from datetime import datetime
from utils import generate_acronym, get_arg, try_msg

import data
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


def desiglar(update, context):
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    message = data.Acronyms.get(arg)
    if message is None:
        message = "🤷"
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def siglar(update, context):
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


def uwuspeech(update, context):
    log_command(update)
    arg = get_arg(update)
    if update.message.reply_to_message and not arg:
        arg = update.message.reply_to_message.text

    message = arg.replace('r', 'w')
                    .replace('l', 'w')
                    .replace('k', 'c')
                    .replace('p', 'pw')
                    .replace('R', 'W')
                    .replace('L', 'W')
                    .replace('K', 'C')
                    .replace('p', 'PW')

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


# Admin Commands

def get_log(update, context):
    log_command(update)
    context.bot.send_document(chat_id=update.message.from_user.id,
                              document=open(os.path.relpath(
                                  'log/bot.log'), 'rb'),
                              filename=f"pasoapasobot_log_{datetime.now().strftime('%d%b%Y-%H%M%S')}.txt")
