import json

import locale

from telegram.ext import CommandHandler, Filters

import data

from bot import updater, dp
from commands import start, tup, desiglar, get_log
from config.auth import admin_ids
from config.logger import logger

locale.setlocale(locale.LC_TIME, "es")

def main():
    try:
        with open("data/acronyms.json", "r", encoding="utf8") as datajsonfile:
            data.acronyms = json.load(datajsonfile)
        logger.info("Acronyms data loaded.")
    except OSError:
        logger.error("Acronyms data not found.")

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('tup', tup))
    dp.add_handler(CommandHandler('desiglar', desiglar))
    # Admin commands
    dp.add_handler(CommandHandler('get_log', get_log, filters=Filters.user(admin_ids)))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
