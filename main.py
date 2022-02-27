# noinspection PyPackageRequirements
from telegram.ext import CommandHandler, Filters

from bot import OfisalitaBot
# from commands import desiglar, siglar, slashear, uwuspeech, get_log
from config.auth import admin_ids


if __name__ == '__main__':
    ofisalita_bot = OfisalitaBot()
    ofisalita_bot.run()
