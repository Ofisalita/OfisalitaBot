# noinspection PyPackageRequirements
from telegram.ext import CommandHandler, Filters

from bot import OfisalitaBot
# from commands import desiglar, siglar, slashear, uwuspeech, get_log
from config.auth import admin_ids


def main():
    dp.add_handler(CommandHandler('desiglar', desiglar))
    dp.add_handler(CommandHandler('siglar', siglar))
    dp.add_handler(CommandHandler('slashear', slashear))
    dp.add_handler(CommandHandler('uwuspeech', uwuspeech))
    # Admin commands
    dp.add_handler(CommandHandler('get_log', get_log,
                                  filters=Filters.user(admin_ids)))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    ofisalita_bot = OfisalitaBot()
    ofisalita_bot.run()
