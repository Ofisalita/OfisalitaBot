import requests
import data
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import CallbackContext
from openai import OpenAI

from commands.decorators import group_exclusive, member_exclusive
from config.logger import log_command
from utils import try_msg, get_arg, num_tokens_from_string

try:
    from config.auth import openai_key
except ImportError:
    openai_key = None

GPT_MODEL = "gpt-4o"
GPT_PRICING_PER_TOKEN = { # https://openai.com/api/pricing/
    "gpt-4o": {"input": 0.000005, "output": 0.000015},
    "gpt-3.5-turbo-0125": {"input": 0.0000005, "output": 0.000015},
    "gpt-3.5-turbo-instruct": {"input": 0.0000015, "output": 0.000020},
}
MAX_MESSAGES_TO_SUMMARIZE = 1000

PROMPT_SYSTEM_MESSAGE_SINGLE = {
    "role": "system",
    "content": "Eres un bot para resumir mensajes de un chat. \
                    Te daré un mensaje y debes resumirlo de forma concisa. No incluyas nada más que el resumen en tu mensaje. Utiliza HTML para los formatos de negritas (<b>) e itálicas (<i>)."
}

PROMPT_SYSTEM_MESSAGE_MULTIPLE = {
    "role": "system",
            "content": "Eres un bot para resumir mensajes de un chat." +
            "Te daré una lista de mensajes en el siguiente formato:\n" +
            "(message_id, username, message, reply_to)\n" +
            "\n" +
            "Donde:\n" +
            "message_id: Identificador único del mensaje.\n" +
            "reply_to: Identificador único del mensaje al que se responde.\n" +
            "username: Nombre de usuario de quien envió el mensaje.\n" +
            "message: El contenido del mensaje.\n" +
            "\n" +
            "Usa esta información para entregar un resumen de lo que se conversó en el chat." +
            "La conversación es informal, en español chileno, puede contener errores gramaticales y ortográficos, utilizar anglicismos y conceptos inventados." +
            "El campo 'reply_to' indica respuestas en la conversación, pero no siempre se utiliza, y los mensajes podrían estar relacionados sin un reply_to explícito." +
            "Al resumir, hazlo como una lista de sucesos relevantes por cada tema de conversación. Usa un lenguaje muy conciso, tipo lista con bullet-points. Cada ítem en la lista es un tema de conversación, con sub-ítemes con algunas conclusiones y resúmenes de las ideas expresadas. Usa los nombres de los usuarios. Utiliza HTML para los formatos de negritas (<b>) e itálicas (<i>).\n" +
            "\n" +
            "Ejemplo\n" +
            "INPUT:\n" +
            "[(123, 34924, 'usuario1', 'ola, hoy vi a Baloian', None)," +
            "(124, 24587, 'usuario2', 'de vdd? qué bacan! lo amoooo, y como estaba?', 123)," +
            "(125, 34924, 'usuario1', 'se veía piola, estaba tomando pap', None)," +
            "(126, 24587, 'usuario2', 'ogh que paja, me carga la pap', None)," +
            "(127, 87562, 'usuario3', 'wena cabros descubrí un framework de js se llama TupJS', None)," +
            "(128, 24587, 'usuario2', 'uuu si lo cacho, apaña caleta pero me gusta más BebJS', 127)," +
            "(129, 34924, 'usuario1', 'que chucha están hablando', None)," +
            "OUTPUT:\n" +
            "<b>Baloian estaba tomando pap</b>\n" +
            "- usuario1 lo vio.\n" +
            "- usuario2 ama a Baloian pero odia la pap.\n" +
            "<b>Conversación sobre frameworks de JS</b>\n" +
            "- usuario3 descubre TupJS.\n" +
            "- usuario2 prefiere BebJS.\n" +
            "- usuario1 no entiende del tema.\n",
}


@group_exclusive
def resumir(update: Update, context: CallbackContext) -> None:
    """
    Summarizes multiples messages from the database.
    """
    log_command(update)

    client = OpenAI(api_key=openai_key)

    # Summarize a specific single replied message
    if not get_arg(update) and update.message.reply_to_message:
        chat_completion = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                PROMPT_SYSTEM_MESSAGE_SINGLE,
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
            parse_mode="HTML",
            text=f"Resumen del [mensaje]({message_link}):\n{result}",
            reply_to_message_id=update.message.message_id,
        )

    # Summarize N messages
    n = None
    try:
        n = int(get_arg(update))
    except ValueError:
        try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            text="Debes indicar la cantidad de mensajes hacia atrás que quieres resumir.",
            reply_to_message_id=update.message.message_id,
        )

    if n and n > MAX_MESSAGES_TO_SUMMARIZE:
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
            reply_to_message_id=update.message.message_id,
        )
        return

    prompt_messages = [
        PROMPT_SYSTEM_MESSAGE_MULTIPLE,
        {
            "role": "user",
            "content": [{"type": "text", "text": str(input_messages)}],
        },
    ]

    prompt_tokens = num_tokens_from_string(str(prompt_messages), GPT_MODEL)
    expected_completion_tokens = 300 # TODO: Calculate this based on the input messages

    try_msg(
        context.bot,
        chat_id=update.message.chat_id,
        text=f"El resumen costará aproximadamente ${round(prompt_tokens * GPT_PRICING_PER_TOKEN[GPT_MODEL]['input'] + expected_completion_tokens * GPT_PRICING_PER_TOKEN[GPT_MODEL]['output'], 5)} USD\n",
        reply_to_message_id=update.message.message_id,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Resumir", callback_data=json.dumps({"callback": "confirm_summary", "n": n, "summarize_from": summarize_from})),
                InlineKeyboardButton(
                    "Cancelar", callback_data=json.dumps({"callback": "cancel_summary"})),
            ],
        ])
    )


def _do_resumir(query: CallbackQuery, context: CallbackContext) -> None:
    client = OpenAI(api_key=openai_key)
    query_data = json.loads(query.data)
    n = query_data["n"]
    summarize_from = query_data["summarize_from"]

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
    prompt_messages = [
        PROMPT_SYSTEM_MESSAGE_MULTIPLE,
        {
            "role": "user",
            "content": [{"type": "text", "text": str(input_messages)}],
        },
    ]

    input_tokens = num_tokens_from_string(str(input_messages), GPT_MODEL)

    chat_completion = client.chat.completions.create(
        model=GPT_MODEL,
        messages=prompt_messages
    )

    result = chat_completion.choices[0].message.content
    start_message_link = f"https://t.me/c/{str(query.message.chat_id)[4:]}/{input_messages[0]['message_id']}"
    end_message_link = f"https://t.me/c/{str(query.message.chat_id)[4:]}/{input_messages[-1]['message_id']}"
    try_msg(
        context.bot,
        chat_id=query.message.chat_id,
        parse_mode="HTML",
        text=f"Resumen de {len(input_messages)} mensajes [<a href=\"{start_message_link}\">Inicio</a> - <a href=\"{end_message_link}\">Fin</a>]:\n" +
             f"<i>Costo: ${round(chat_completion.usage.prompt_tokens * GPT_PRICING_PER_TOKEN[GPT_MODEL]['input'] + chat_completion.usage.completion_tokens * GPT_PRICING_PER_TOKEN[GPT_MODEL]['output'], 5)} USD</i>\n" +
             f"<i>Tokens input: {input_tokens}, Tokens output: {chat_completion.usage.completion_tokens}, Ratio: {input_tokens/int(chat_completion.usage.completion_tokens)}</i>\n\n" +
             str(result),
        reply_to_message_id=query.message.reply_to_message.message_id,
    )

# TODO: Refactor. This receives all callback queries, not just the ones from the summary command.
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data = json.loads(query.data)
    # Only requesting user can answer
    if query.message.reply_to_message.from_user.id != query.from_user.id:
        query.answer("Solo quien solicitó el resumen puede confirmarlo.")
        return
    else:
        query.answer()
        if query_data["callback"] == "confirm_summary":
            query.edit_message_text(
                text=f"{query.message.text}\n\nResumen aceptado. Procesando...")
            _do_resumir(query, context)
        elif query_data["callback"] == "cancel_summary":
            query.edit_message_text(
                text=f"{query.message.text}\n\nResumen cancelado.")


# Debug
@ member_exclusive
def get_last_n(update: Update, context: CallbackContext) -> None:
    """
    Gets the last N messages from the database.
    """
    log_command(update)

    n = int(get_arg(update))
    messages = data.Messages.get_n(n)
