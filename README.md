# OfisalitaBot

- [Contibuir al Bot](#contribución)
- [Usar el Bot](#uso)

## Contribución

### Micro-tutorial

Para agregar un comando, se debe agregar el [Handler](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.html#handlers) apropiado en `main.py`. El más común es [`CommandHandler`](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.html#handlers), que parsea los mensajes de tipo `/comando`. A este handler se le da la función de callback que llamará, y ésta debe ir en un archivo `.py` en la carpeta `commands`. En esa función se puede hacer lo que sea que Python pueda hacer.

Para mandar un mensaje está creada la función `try_msg` en los `utils`, que es solamente un proxy de la función real ([`context.bot.send_message`](https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html#telegram.Bot.send_message)) y su gracia es que se le puede dar un número de attempts para re-intentar el envío. Esto está hecho porque existe un bug en el que si el bot está inactivo por un tiempo, el siguiente mensaje falla uwu.

El comando más simple es `tup` en `commands/response.py`. Revisarlo para ver un ejemplo de cómo se hace.

Los comandos ya establecidos tienen el decorador `@member_exclusive` que se encarga de verificar que el usuario que ejecuta el comando es miembro del grupo. Si no lo es, no se ejecuta el comando. Si estás corriendo localmente el bot, puedes cambiar el valor `debug` en `config/auth.py` a `True` para que no verifique esto.

### Estructura

- `config`
  - `auth.py`: Constantes relacionadas a la autenticación del bot y usuarios (e.g. token del bot, IDs de admins). No está en el repo **Y NO DEBERÍA ESTAR**, porque el token es privadest.
  - `db.py`: Configuración relacionada a la base de datos.
  - `logger.py`: Configuración relacionada al logging del bot.
  - `persistence.py`: Configuración de la persistencia, i.e. cómo guardar la base de datos interna del bot (user_data, chats_data).
- `data`
  - `db.sqlite3`: Ruta por defecto de la base de datos.
- `main.py`: Carga la data necesaria, asigna los comandos disponibles e inicializa el polling del bot.
- `commands`: Define las funciones que se ejecutan cuando se usa un comando de Telegram, asignados en `main.py`.
  - `acronyms.py`: Comandos relacionados a las siglas.
  - `admin.py`: Comandos relacionados a la administración del bot.
  - `counter.py`: Comandos relacionados a contadores numéricos.
  - `list.py`: Comandos relacionados a listas de cosas.
  - `response.py`: Comandos relacionados a responder a ciertos mensajes.
  - `text.py`: Comandos relacionados a alterar texto.
  - `weather.py`: Comandos de predicción del clima.
- `data.py`: Define las funciones para interactuar con SQLite.
- `bot.py`: Contiene el [Updater](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.updater.html) que controla el bot y variables relacionadas.
- `functions.py`: Funciones auxiliares complejas y específicas de cierta funcionalidad. e.g. load/save de data, web querying, scrappers, etc.
- `utils.py`: Funciones auxiliares genéricas abstraídas para facilitar sintáxis. e.g. manejo de strings, conversión de formatos, etc.
- `root.py`: Sirve de anca para el directorio del bot.

## Uso

### Siglas

Se pueden registar siglas y su significado, y luego usarlas en cualquier mensaje para que el bot las convierta en su significado.

- `/siglar [text | reply]` - Convierte el argumento en una sigla, y lo guarda a la base de datos.
- `/desiglar [text | reply]` - Convierte el argumento (sigla) en su texto corresponidente.
- `/glosario [l]` - Muestra el glosario de siglas, con la opción de filtrar por letra.

### Contadores

Se pueden crear mensajes que son contadores numéricos. A estos contadores se les puede sumar o restar un valor.

- `/contador [text]` - Crear un mensaje tipo contador, con el texto dado como título.
- `/[sumar | incrementar] [number] (reply)` - Incrementa el contador al que se responde, con 1 o el valor que se le da.
- `/[restar | decrementar] [number] (reply)` - Decrementa el contador al que se responde, con 1 o el valor que se le da.

### Listas

Se pueden crear mensajes que son listas. A estas listas se les puede agregar, quitar o editar items colaborativamente.

- `/[lista | listar] [text]` - Crea una lista con el texto dado como título.
- `/agregar [text] (reply)` - Agrega el texto dado como item a la lista a la que se responde.
- `/quitar [index] (reply)` - Quita el item del índice dado de la lista a la que se responde.
- `/editar [index] [text] (reply)` - Edita el item del índice dado de la lista a la que se responde, con el texto dado.
- `/[deslistar | cerrar] (reply)` - Hace ineditable la lista a la que se responde.

### Respuestas

Comandos que instan al bot a responder algo particular.

- `/start` - Responde un saludo.
- `/tup` - Responde "tup".
- `/[gracias | garcias]` - Responde un sticker de "denarda".
- `/asistencia` - Responde con un poll de días de la semana para ver cuándo asiste cada persona.
- `/hello` - Responde como reply al mensaje al que se responde.

### Texto

Comandos que toman un texto, y lo modifican o procesan de alguna forma.

- `/slashear (reply)` - Responde con el texto del mensaje al que se responde en un texto camel case con un slash.
- `/['uwuspeech' | 'uwuspeak' | 'uwuizar' | 'uwu'] [text | reply]` - Responde con el texto del mensaje al que se responde en un texto uwu-ificado.
- `/repetir [text | reply]` - Responde con el mismo texto del argumento.
- `/distancia (reply)` - Responde con la cantidad de mensajes que se han enviado entre la invocación y el mensaje al que se le está haciendo reply.

### OpenAI/GPT

- `/gpt [text | reply]` - Genera una respuesta al texto del argumento. Usa el modelo Anthropic Claude Sonnet.
- `/gb [text | reply]` - Rellena los guiones bajos del texto del argumento, usando el modelo Anthropic Claude Sonnet. A veces cambia un poco el texto original.
- `/desigliar [text | reply]` - Inventa una desiglación para una sigla usando el modelo Anthropic Claude Sonnet.

### Clima

Esta funcionalidad compara el clima de ayer con el de hoy, enviando un reporte diario a una hora fija.

- `/habilitar_clima` - Habilita/Deshabilita los reportes del clima.

### Admin

- `/get_log` - Muestra el log del bot por interno a los IDs configurados como admins.
- `/prohibir (reply)` - Hace que el bot elimine el mensaje al que se le responde (solo mensajes del bot).
