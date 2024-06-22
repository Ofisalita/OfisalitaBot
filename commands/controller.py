import re

from telegram import Update, constants as tg_constants
from telegram.ext import CallbackContext

from utils import try_msg, send_long_message

class CommandController:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self._parse()

    def _parse(self):
        match = re.match(
            r"^(?P<command>\/\w+)(?:\[(?P<opts>.*)\])?(?: (?P<arg>.*))?$",
            self.update.message.text,
            re.DOTALL,
        )
        if match:
            parsed = match.groupdict()
            self.command = parsed["command"]
            self.opts = parsed["opts"]
            self.arg = parsed["arg"]
        else:
            raise ValueError("Invalid command format.")

    def __getattr__(self, name):
        return getattr(self.update.message, name)

    def send_message(self, text, **kwargs):
        send_func = try_msg
        if len(text) > tg_constants.MAX_MESSAGE_LENGTH:
            send_func = send_long_message
        send_func(
            self.context.bot,
            chat_id=self.update.message.chat_id,
            text=text,
            reply_to_message_id=self.update.message.message_id,
            **kwargs,
        )
    
