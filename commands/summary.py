import requests
import data

from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import member_exclusive
from config.logger import log_command
from utils import try_msg, get_arg

try:
    from config.auth import openai_key
except ImportError:
    openai_key = None


@member_exclusive
def resumir(update: Update, context: CallbackContext) -> None:
    """
    Attempts to summarize a given text
    """
    log_command(update)

    n = get_arg(update)

    summarize_from = None
    if update.message.reply_to_message:
        summarize_from = update.message.reply_to_message.message_id
    reply_message_id = update.message.message_id

    raw_messages = data.Messages.get_n(int(n), from_id=summarize_from)
    print(raw_messages)
    input_messages = [
        {
            "message_id": m["message_id"],
            "username": m["username"],
            "message": m["message"],
            "reply_to": m["reply_to"],
        }
        for m in raw_messages
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}",
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "Eres un bot para resumir mensajes de un chat. \
                Te daré una lista de mensajes en el siguiente formato: \n \
                (message_id, username, message, reply_to)\n\
                \n\
                Donde:\n\
                message_id: Identificador único del mensaje.\n\
                reply_to: Identificador único del mensaje al que se responde.\n\
                username: Nombre de usuario de quien envió el mensaje.\n\
                message: El contenido del mensaje.\n\
                \n\
                Usa esta información para entregar un resumen de lo que se conversó en el chat.\
                La conversación es informal, en español chileno, puede contener errores gramaticales y ortográficos, utilizar anglicismos y conceptos inventados.\
                El campo 'reply_to' indica respuestas en la conversación, pero no siempre se utiliza, y los mensajes podrían estar relacionados sin un reply_to explícito.\
                Al resumir, hazlo como una lista de sucesos relevantes por cada tema de conversación. Usa un lenguaje muy conciso, tipo lista con bullet-points. Cada ítem en la lista es un tema de conversación, con sub-ítemes con algunas conclusiones y resúmenes de las ideas expresadas. Usa los nombres de los usuarios.\n\
                \n\
                Ejemplo\n\
                INPUT:\n\
                [(123, 34924, 'usuario1', 'ola, hoy vi a Baloian', None),\
                (124, 24587, 'usuario2', 'de vdd? qué bacan! lo amoooo, y como estaba?', 123),\
                (125, 34924, 'usuario1', 'se veía piola, estaba tomando pap', None),\
                (126, 24587, 'usuario2', 'ogh que paja, me carga la pap', None),\
                (127, 87562, 'usuario3', 'wena cabros descubrí un framework de js se llama TupJS', None),\
                (128, 24587, 'usuario2', 'uuu si lo cacho, apaña caleta pero me gusta más BebJS', 127),\
                (129, 34924, 'usuario1', 'que chucha están hablando', None),\
                OUTPUT:\n\
                *Baloian estaba tomando pap*\n\
                -- usuario1 lo vio.\n\
                -- usuario2 ama a Baloian pero odia la pap.\n\
                *Conversación sobre frameworks de JS*\n\
                -- usuario3 descubre TupJS.\n\
                -- usuario2 prefiere BebJS.\n\
                -- usuario1 no entiende del tema.\n",
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": str(input_messages)}],
            },
        ],
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response = response.json()
    print(response)
    result = response["choices"][0]["message"]["content"]

    start_message_link = f"https://t.me/c/{str(update.message.chat_id)[4:]}/{input_messages[0]['message_id']}"
    end_message_link = f"https://t.me/c/{str(update.message.chat_id)[4:]}/{input_messages[-1]['message_id']}"
    try_msg(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="Markdown",
        text=f"Resumen de {n} mensajes:\n[[Inicio]({start_message_link}) - [Fin]({end_message_link})]\n{result}",
        reply_to_message_id=reply_message_id,
    )


# Debug
@member_exclusive
def get_last_n(update: Update, context: CallbackContext) -> None:
    """
    Gets the last N messages from the database.
    """
    log_command(update)

    n = get_arg(update)
    messages = data.Messages.get_n(n)

    print(messages)
