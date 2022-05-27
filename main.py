from telegram.ext import CommandHandler, Filters

import data
from bot import updater, dp
from commands import start, tup, desiglar, siglar, slashear, uwuspeech, \
                        repetir, lista, agregar, quitar, get_log, contador, \
                        sumar, restar, deslistar
from config.auth import admin_ids


def main():
    data.init()

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('tup', tup))
    dp.add_handler(CommandHandler('desiglar', desiglar))
    dp.add_handler(CommandHandler('siglar', siglar))
    dp.add_handler(CommandHandler('slashear', slashear))
    dp.add_handler(CommandHandler('uwuspeech', uwuspeech))
    dp.add_handler(CommandHandler('uwuspeak', uwuspeech))
    dp.add_handler(CommandHandler('uwuizar', uwuspeech))
    dp.add_handler(CommandHandler('uwu', uwuspeech))

    dp.add_handler(CommandHandler('repetir', repetir))
    dp.add_handler(CommandHandler('lista', lista))
    dp.add_handler(CommandHandler('agregar', agregar))
    dp.add_handler(CommandHandler('quitar', quitar))
    dp.add_handler(CommandHandler('deslistar', deslistar))

    dp.add_handler(CommandHandler('contador', contador))
    dp.add_handler(CommandHandler('sumar', sumar))
    dp.add_handler(CommandHandler('incrementar', sumar))
    dp.add_handler(CommandHandler('restar', restar))
    dp.add_handler(CommandHandler('decrementar', restar))

    # Admin commands
    dp.add_handler(CommandHandler('get_log', get_log,
                                  filters=Filters.user(admin_ids)))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
