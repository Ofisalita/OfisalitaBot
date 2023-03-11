import os
from datetime import datetime

from telegram import Update, ParseMode, constants
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

import data
from config.logger import log_command
from utils import generate_acronym, get_arg, reverse_acronym, try_msg, \
    try_edit, guard_editable_bot_message, member_check


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

# --- Acronym Commands ---


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
        message = reverse_acronym(arg.lower())
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


def glosario(update: Update, context: CallbackContext) -> None:
    """Sends a list of acronyms and meanings to the private chat
    of the user that called the command."""

    log_command(update)

    if not member_check(update, context):
        return

    arg = get_arg(update)

    if arg:
        if len(arg) > 1:
            try_msg(context.bot,
                    chat_id=update.message.chat_id,
                    parse_mode="HTML",
                    text="Este comando sólo puede invocarse "
                         "con 1 (un) caracter o ninguno.")
            return
        acronyms = data.Acronyms.list_by_letter(arg.lower())
        if not acronyms:
            try_msg(context.bot,
                    chat_id=update.message.chat_id,
                    parse_mode="HTML",
                    text=f"No encontré siglas que empiecen con {arg} :^(")
            return
    else:
        acronyms = data.Acronyms.list_all()

    acronyms.sort(key=lambda x: x[0])

    if update.message.from_user.id != update.message.chat_id:
        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=f"Enviaré la lista de siglas a tu chat privado ;^)")

    separator = f"\n➖➖➖➖➖➖➖"
    msg = separator

    for idx, acro in enumerate(acronyms):
        definition = f"\n{acro[0]}\n{acro[1]}"

        if len(msg + definition + separator) > constants.MAX_MESSAGE_LENGTH:
            try_msg(context.bot,
                    chat_id=update.message.from_user.id,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    text=escape_markdown(msg, version=2),
                    disable_web_page_preview=True)
            msg = separator

        msg += definition + separator

        if idx == len(acronyms) - 1:
            try_msg(context.bot,
                    chat_id=update.message.from_user.id,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    text=escape_markdown(msg, version=2),
                    disable_web_page_preview=True)


# --- List Commands ---
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
    # If the user didn't specify a number, then the command is invalid
    except ValueError:
        return

    new_content = args[args.find(" ") + 1:]
    lines = content.split("\n")

    # if the number is 0 edit the title
    if number == 0:
        lines[0] = f"{LIST_HASHTAG} {new_content}:"
    # if the number is an item from the list, edit it
    elif number in range(1, len(lines) + 1):
        lines[number] = f"{number}- {new_content}"
    # if the number is out of range or any other border case, just ignore it
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

# --- End of List Commands ---


# --- Counter Commands ---
COUNTER_HASHTAG = "#CONTADOR"


def contador(update: Update, context: CallbackContext) -> None:
    """
    Starts an editable counter
    """
    log_command(update)
    arg = get_arg(update).replace("\n", " ")
    message = f"{COUNTER_HASHTAG} {arg}:\n0"

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


def sumar(update: Update, context: CallbackContext, sign: int = 1) -> None:
    """
    Adds a number to a counter (default 1)
    """
    if guard_editable_bot_message(update, context, COUNTER_HASHTAG):
        return

    content = update.message.reply_to_message.text
    lines = content.split("\n")

    previous_number = int(lines[-1])

    argument = get_arg(update)
    if not argument:
        addition = 1
    else:
        addition = int(get_arg(update))

    addition *= sign

    lines[-1] = previous_number + addition

    new_message = "\n".join([str(item) for item in lines])

    try_edit(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        message_id=update.message.reply_to_message.message_id,
        text=new_message
    )


def restar(update: Update, context: CallbackContext) -> None:
    """
    Subtracts a number to a counter (default 1)
    """
    sumar(update, context, -1)

# --- End of Counter Commands

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
