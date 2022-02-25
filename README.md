# OfisalitaBot

## Micro-tutorial
Para agregar un comando, se debe agregar el [Handler](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.html#handlers) apropiado en `main.py`. El más común es [`CommandHandler`](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.html#handlers), que parsea los mensajes de tipo `/comando`. A este handler se le da la función de callback que llamará, y ésta debe ir en `commands.py`. En esa función se puede hacer lo que sea que Python pueda hacer.

Para mandar un mensaje está creada la función `try_msg` en los `utils`, que es solamente un proxy de la función real ([`context.bot.send_message`](https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html#telegram.Bot.send_message)) y su gracia es que se le puede dar un número de attempts para re-intentar el envío. Esto está hecho porque existe un bug en el que si el bot está inactivo por un tiempo, el siguiente mensaje falla uwu.

El comando más simple es `tup`. Revisarlo para ver un ejemplo de cómo se hace.

## Estructura
- `config`
  - `auth.py`: Constantes relacionadas a la autenticación del bot y usuarios (e.g. token del bot, IDs de admins). No está en el repo **Y NO DEBERÍA ESTAR**, porque el token es privadest.
  - `db.py`: Configuración relacionada a la base de datos.
  - `logger.py`: Configuración relacionada al logging del bot.
  - `persistence.py`: Configuración de la persistencia, i.e. cómo guardar la base de datos interna del bot (user_data, chats_data).
- `data`
  - `db.sqlite3`: Ruta por defecto de la base de datos.
- `main.py`: Carga la data necesaria, asigna los comandos disponibles e inicializa el polling del bot.
- `commands.py`: Define las funciones que se ejecutan cuando se usa un comando de Telegram, asignados en `main.py`.
- `data.py`: Define las funciones para interactuar con SQLite.
- `bot.py`: Contiene el [Updater](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.updater.html) que controla el bot y variables relacionadas.
- `functions.py`: Funciones auxiliares complejas y específicas de cierta funcionalidad. e.g. load/save de data, web querying, scrappers, etc.
- `utils.py`: Funciones auxiliares genéricas abstraídas para facilitar sintáxis. e.g. manejo de strings, conversión de formatos, etc.
