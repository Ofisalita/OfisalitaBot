import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext
from utils import generate_acronym, get_arg, reverse_acronym, try_msg, try_edit

import data
from config.logger import log_command


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


def slashear(update, context):
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


def repeat(update: Update, context: CallbackContext) -> None:
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


def startlist(update: Update, context: CallbackContext) -> None:
    """
    Starts an editable list
    """
    log_command(update)
    arg = get_arg(update)
    message = f"#list {arg}:"

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def add(update: Update, context: CallbackContext) -> None:
    """
    Adds an item to a list
    """
    if not update.message.reply_to_message:
        return

    if context.bot.id != update.message.reply_to_message.from_user.id:
        return

    content = update.message.reply_to_message.text

    if not content.startswith("#list"):
        return

    lines = content.split("\n")
    lines_count = len(lines)

    addition = get_arg(update).replace("\n", " ")

    new_message = content + f"\n{lines_count}- " + addition

    try_edit(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        message_id=update.message.reply_to_message.message_id,
        text=new_message
    )


def remove(update: Update, context: CallbackContext) -> None:
    """
    Removes an item from a list
    """
    if not update.message.reply_to_message:
        return

    if context.bot.id != update.message.reply_to_message.from_user.id:
        return

    content = update.message.reply_to_message.text

    if not content.startswith("#list"):
        return

    number = int(get_arg(update))
    number_dash = str(number) + "-"

    lines = content.split("\n")
    new_lines = []

    found_target = False
    for line in lines:
        if found_target:
            split_line = line.split("- ")
            number = str(int(split_line[0]) - 1)
            split_line[0] = number
            new_lines.append('- '.join(split_line))
        else:
            if line.startswith(number_dash):
                found_target = True
            else:
                new_lines.append(line)

    new_message = '\n'.join(new_lines)

    try_edit(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        message_id=update.message.reply_to_message.message_id,
        text=new_message
    )


# Admin Commands


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
