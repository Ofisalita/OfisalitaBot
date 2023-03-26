from telegram import Update, ParseMode, constants
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

import data
from commands.decorators import member_exclusive
from config.logger import log_command
from utils import get_arg, try_msg, reverse_acronym, \
    generate_acronym


@member_exclusive
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


@member_exclusive
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


@member_exclusive
def glosario(update: Update, context: CallbackContext) -> None:
    """Sends a list of acronyms and meanings to the private chat
    of the user that called the command."""

    log_command(update)
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
                text="Enviaré la lista de siglas a tu chat privado ;^)")

    separator = "\n➖➖➖➖➖➖➖"
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
