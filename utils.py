from telegram import Update, Bot, TelegramError, constants as tg_constants

from config.logger import logger


def try_msg(bot: Bot, attempts: int = 2, **params) -> None:
    """
    Make multiple attempts to send a message.
    """
    chat_id = params["chat_id"]
    attempt = 1
    while attempt <= attempts:
        try:
            bot.send_message(**params)
        except TelegramError as e:
            logger.error((
                    f"[Attempt {attempt}/{attempts}] Messaging chat {chat_id} "
                    f"raised following error: {type(e).__name__}: {e}"
                )
            )
        else:
            break
        attempt += 1

    if attempt > attempts:
        logger.error((
                f"Max attempts reached for chat {str(chat_id)}."
                "Aborting message and raising exception."
            )
        )


def send_long_message(bot: Bot, **params) -> None:
    """
    Recursively breaks long texts into multiple messages,
    prioritizing newlines for slicing.
    """
    text = params.pop("text", "")

    params_copy = params.copy()
    maxl = params.pop("max_length", tg_constants.MAX_MESSAGE_LENGTH)
    slice_str = params.pop("slice_str", "\n")
    if len(text) > maxl:
        slice_index = text.rfind(slice_str, 0, maxl)
        if slice_index <= 0:
            slice_index = maxl
        sliced_text = text[:slice_index]
        rest_text = text[slice_index + 1:]
        try_msg(bot, text=sliced_text, **params)
        send_long_message(bot, text=rest_text, **params_copy)
    else:
        try_msg(bot, text=text, **params)


def get_arg(update: Update) -> str:
    try:
        arg = update.message.text[(update.message.text.index(" ") + 1):]
    except ValueError:
        arg = ""
    return arg


def generate_acronym(string: str) -> str:
    string_list = string.split()
    out = ""
    for word in string_list:
        out += word[0]
        if word.find("?") > 0:
            out += "?"
    return out.lower()
