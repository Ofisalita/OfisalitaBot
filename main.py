from telegram.ext import CommandHandler, Filters

import data
from bot import updater, dp
from config.auth import admin_ids

from commands.acronym import desiglar, siglar, glosario
from commands.admin import get_log
from commands.counter import contador, sumar, restar
from commands.list import lista, agregar, quitar, editar, deslistar
from commands.response import start, tup, gracias
from commands.text import slashear, uwuspeech, repetir


def main():
    data.init()

    # ==== Acronym
    dp.add_handler(CommandHandler('desiglar', desiglar))
    dp.add_handler(CommandHandler('siglar', siglar))
    dp.add_handler(CommandHandler('glosario', glosario))

    # ==== Admin
    dp.add_handler(CommandHandler('get_log', get_log,
                                  filters=Filters.user(admin_ids)))

    # ==== Counter
    dp.add_handler(CommandHandler('contador', contador))
    dp.add_handler(CommandHandler('sumar', sumar))
    dp.add_handler(CommandHandler('incrementar', sumar))
    dp.add_handler(CommandHandler('restar', restar))
    dp.add_handler(CommandHandler('decrementar', restar))

    # ==== List
    dp.add_handler(CommandHandler('lista', lista))
    dp.add_handler(CommandHandler('agregar', agregar))
    dp.add_handler(CommandHandler('quitar', quitar))
    dp.add_handler(CommandHandler('editar', editar))
    dp.add_handler(CommandHandler('deslistar', deslistar))
    dp.add_handler(CommandHandler('cerrar', deslistar))

    # ==== Text
    dp.add_handler(CommandHandler('uwuspeech', uwuspeech))
    dp.add_handler(CommandHandler('uwuspeak', uwuspeech))
    dp.add_handler(CommandHandler('uwuizar', uwuspeech))
    dp.add_handler(CommandHandler('uwu', uwuspeech))
    dp.add_handler(CommandHandler('slashear', slashear))
    dp.add_handler(CommandHandler('repetir', repetir))

    # ==== Response
    dp.add_handler(CommandHandler('tup', tup))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('gracias', gracias))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
