import functools
from typing import Callable

from telegram import Update
from telegram.ext import CallbackContext

from config.auth import group_id
from config.logger import logger
from utils import try_msg


def member_exclusive(func: Callable):
    """Decorator that checks whether the update was sent by a member of the
    group configured in auth.py. If it wasn't, sends a "forbidden" message.
    """

    @functools.wraps(func)
    def member_check(update: Update, context: CallbackContext) -> None:
        chat_member = context.bot.getChatMember(group_id,
                                                update.message.from_user.id)

        if chat_member.status not in ["administrator", "creator", "member"]:
            try_msg(context.bot,
                    chat_id=update.message.chat_id,
                    parse_mode="HTML",
                    text="<b>403 FORBIDDEN</b>")
            logger.warning((
                f"[NOT A MEMBER] [Command '{update.message.text}' "
                f"was called by {update.message.chat_id}]"
            ))
            return

        func(update, context)
        return

    return member_check
