import re
import json

from telegram import Message, CallbackQuery
from utils import strip_quotes


class Command:
    """
    This object represents a bot command.
    Takes care of basic command functionality, such as parsing and logging.
    """

    def __init__(self, message: Message):
        self.message_obj = message
        parsed = self._parse()
        self.command = parsed["command"]
        self.opts = self._parse_opts(parsed["opts"])
        self.arg = parsed["arg"]

    def _parse(self):
        """
        Parses a command message and returns a dictionary with the command,
        options and argument (text).
        """
        match = re.match(
            r"^(?P<command>\/\w+)(?:\((?P<opts>.*?)\))?(?: (?P<arg>.*))?$",
            self.message_obj.text,
            re.DOTALL,
        )
        if match:
            return match.groupdict()
        else:
            raise ValueError("Invalid command format.")

    def _parse_opts(self, opts):
        """
        Parses the options string and returns a dictionary.
        """
        if not opts:
            return {}
        # Regex to split by commas and equals, but not within quotes
        commas_regex = r'(?!\B"[^"]*),(?![^"]*"\B)'
        equals_regex = r'(?!\B"[^"]*)=(?![^"]*"\B)'

        # Split by comma to get options
        opts_split = re.split(commas_regex, opts)

        # Split by equals to get key-value pairs
        opts_pairs = []
        for o in [re.split(equals_regex, opt) for opt in opts_split]:
            if len(o) != 2:
                # If there is no value, assume it's a boolean flag
                o = (o[0], str(True))
            key = strip_quotes(o[0].strip())
            value = strip_quotes(o[1].strip())
            opts_pairs.append((key, value))
        opts_dict = dict(opts_pairs)
        return opts_dict

    def get_arg_reply(self) -> str:
        """
        Returns the argument of a command or the text of a reply.
        (Preference towards replies)
        """
        if self.message_obj.reply_to_message:
            return self.message_obj.reply_to_message.text
        return self.arg

    def use_default_opt(self, default_key: str):
        """
        If only a single flag option is provided, assume it's the default key.

        e.g. /command(Hello guys!) -> /command([default_key]=Hello guys!)
        """
        if len(self.opts.values()) == 1 and list(self.opts.values())[0] == "True":
            self.opts = {default_key: list(self.opts.keys())[0]}


class CallbackQueryCommand(Command):
    """
    Fake Command object to parse CallbackQuery objects.
    """

    def __init__(self, query: CallbackQuery):
        super().__init__(query.message)

    def _parse(self):
        opts = re.search(r"OPTS: (\{.*\})", self.message_obj.text)
        opts = opts.group(1) if opts else None
        return {"command": None, "opts": opts, "arg": None}

    def _parse_opts(self, opts):
        return json.loads(opts) if opts else {}

    def get_arg_reply(self) -> str:
        pass
