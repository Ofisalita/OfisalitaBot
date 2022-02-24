import locale

from telegram.ext import CommandHandler, Filters

from bot import updater, dp
from commands import start, tup, get_log
from config.auth import admin_ids

locale.setlocale(locale.LC_TIME, "es")

def main():
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('tup', tup))
    # Admin commands
    dp.add_handler(CommandHandler('get_log', get_log, filters=Filters.user(admin_ids)))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
