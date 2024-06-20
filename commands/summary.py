import requests
import data

from telegram import Update
from telegram.ext import CallbackContext
from openai import OpenAI

from commands.decorators import group_exclusive, member_exclusive
from config.logger import log_command
from utils import try_msg, get_arg

try:
    from config.auth import openai_key
except ImportError:
    openai_key = None

GPT_MODEL = "gpt-4o"
MAX_MESSAGES_TO_SUMMARIZE = 100


@group_exclusive
def resumir(update: Update, context: CallbackContext) -> None:
    """
    Attempts to summarize a given text
    """
    log_command(update)

    client = OpenAI(openai_key)

    # Summarize a specific single message
    if not get_arg(update) and update.message.reply_to_message:
        chat_completion = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un bot para resumir mensajes de un chat. \
                    Te daré un mensaje y debes resumirlo de forma concisa. No incluyas nada más que el resumen en tu mensaje."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": update.message.reply_to_message.text,
                        }
                    ],
                }
            ]
        )
        result = chat_completion.choices[0].message.content
        message_link = f"https://t.me/c/{str(update.message.chat_id)[4:]}/{update.message.reply_to_message.message_id}"
        try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            parse_mode="Markdown",
            text=f"Resumen del [mensaje]({message_link}):\n{result}",
            reply_to_message_id=update.message.message_id,
        )

    # Summarize N messages
    n = int(get_arg(update))

    if n > MAX_MESSAGES_TO_SUMMARIZE:
        try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            text=f"No puedo resumir más de {MAX_MESSAGES_TO_SUMMARIZE} mensajes a la vez.",
            reply_to_message_id=update.message.message_id,
        )
        return

    summarize_from = None
    if update.message.reply_to_message:
        summarize_from = update.message.reply_to_message.message_id
    reply_message_id = update.message.message_id

    raw_messages = data.Messages.get_n(n, from_id=summarize_from)
    input_messages = [
        {
            "message_id": m["message_id"],
            "username": m["username"],
            "message": m["message"],
            "reply_to": m["reply_to"],
        }
        for m in raw_messages
    ]

    if not input_messages:
        try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            text="No encontré mensajes para resumir. Es posible que lo que intentas resumir no haya sido registrado en la base de datos.",
            reply_to_message_id=reply_message_id,
        )
        return

    chat_completion = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
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
                - usuario1 lo vio.\n\
                - usuario2 ama a Baloian pero odia la pap.\n\
                *Conversación sobre frameworks de JS*\n\
                - usuario3 descubre TupJS.\n\
                - usuario2 prefiere BebJS.\n\
                - usuario1 no entiende del tema.\n",
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": str(input_messages)}],
            },
        ]
    )

    result = chat_completion.choices[0].message.content
    start_message_link = f"https://t.me/c/{str(update.message.chat_id)[4:]}/{input_messages[0]['message_id']}"
    end_message_link = f"https://t.me/c/{str(update.message.chat_id)[4:]}/{input_messages[-1]['message_id']}"
    try_msg(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="Markdown",
        text=f"Resumen de {len(input_messages)} mensajes:\n" +
             f"[[Inicio]({start_message_link}) - [Fin]({end_message_link})]\n" +
             str(result),
        reply_to_message_id=reply_message_id,
    )


# Debug
@member_exclusive
def get_last_n(update: Update, context: CallbackContext) -> None:
    """
    Gets the last N messages from the database.
    """
    log_command(update)

    n = int(get_arg(update))
    messages = data.Messages.get_n(n)

    print(messages)
