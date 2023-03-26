from telegram import Update
from telegram.ext import CallbackContext

from config.logger import log_command
from utils import get_arg, try_msg, guard_editable_bot_message, try_edit


LIST_HASHTAG = "#LISTA"


def lista(update: Update, context: CallbackContext) -> None:
    """
    Starts an editable list
    """
    log_command(update)
    arg = get_arg(update)
    message = f"{LIST_HASHTAG} {arg}:"

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def agregar(update: Update, context: CallbackContext) -> None:
    """
    Adds an item to a list
    """
    if guard_editable_bot_message(update, context, LIST_HASHTAG):
        return

    content = update.message.reply_to_message.text
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


def quitar(update: Update, context: CallbackContext) -> None:
    """
    Removes an item from a list
    """
    if guard_editable_bot_message(update, context, LIST_HASHTAG):
        return

    content = update.message.reply_to_message.text

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


def editar(update: Update, context: CallbackContext) -> None:
    """
    Edits an item from a list
    """
    log_command(update)
    if guard_editable_bot_message(update, context, LIST_HASHTAG):
        return

    content = update.message.reply_to_message.text
    args = get_arg(update)

    try:
        number = int(args[:args.find(" ")])
    except ValueError:
        return

    new_content = args[args.find(" ") + 1:]
    lines = content.split("\n")

    if number == 0:
        lines[0] = f"{LIST_HASHTAG} {new_content}:"
    elif number in range(1, len(lines) + 1):
        lines[number] = f"{number}- {new_content}"
    else:
        return

    new_message = '\n'.join(lines)

    if new_message == content:
        return

    try_edit(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        message_id=update.message.reply_to_message.message_id,
        text=new_message
    )


def deslistar(update: Update, context: CallbackContext) -> None:
    """
    Cierra una lista
    """
    if guard_editable_bot_message(update, context, LIST_HASHTAG):
        return

    content = update.message.reply_to_message.text
    new_message = content[1:]

    try_edit(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        message_id=update.message.reply_to_message.message_id,
        text=new_message
    )
