import data
import json
import re
import math
import feedparser
import urllib

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from telegram.ext import CallbackContext

from ai.provider import ai_client
from ai.base import GenAIMessage
import ai.pricing as prc
from ai.models import RESUMIR_MODEL, QUEPASO_MODEL
from commands.base import Command, CallbackQueryCommand
from commands.decorators import command
from utils import (
    num_tokens_from_string,
    get_alias_dict_from_string,
    get_alias_dict_from_messages_list,
    anonymize,
    deanonymize,
    try_msg,
)

MAX_MESSAGES_TO_SUMMARIZE = 1000

PROMPT_SYSTEM_MESSAGE_SINGLE = (
    "Eres un bot para resumir mensajes de un chat. "
    + "Te daré un mensaje y debes resumirlo de forma concisa. No incluyas nada más que el resumen en tu mensaje. "
    + "Utiliza HTML para los formatos de <b>negritas</b> e <i>itálicas</i>, NO uses otras etiquetas aparte de <b> y <i>. NO uses Markdown."
)

PROMPT_SYSTEM_MESSAGE_MULTIPLE = (
    "Eres un bot para resumir mensajes de un chat. "
    + "Te daré una lista de mensajes en el siguiente formato:\n"
    + "(message_id, username, message, reply_to)\n"
    + "\n"
    + "Donde:\n"
    + "message_id: Identificador único del mensaje.\n"
    + "reply_to: Identificador único del mensaje al que se responde.\n"
    + "username: Nombre de usuario de quien envió el mensaje.\n"
    + "message: El contenido del mensaje.\n"
    + "\n"
    + "Usa esta información para entregar un resumen de lo que se conversó en el chat.\n"
    + "La conversación es informal, en español chileno, puede contener errores gramaticales y ortográficos, utilizar anglicismos y conceptos inventados.\n"
    + "El campo 'reply_to' indica respuestas en la conversación, pero no siempre se utiliza, y los mensajes podrían estar relacionados sin un reply_to explícito.\n"
    + "Al resumir, hazlo como una lista de sucesos relevantes por cada tema de conversación. Usa un lenguaje muy conciso, tipo lista con bullet-points. Cada ítem en la lista es un tema de conversación, con sub-ítemes con algunas conclusiones y resúmenes de las ideas expresadas. Usa los nombres de los usuarios. Utiliza HTML para los formatos de negritas (<b>) e itálicas (<i>).\n"
    + "Ignora todo lo que diga '{OPTS: ...}'\n"
    + "\n"
    + "Ejemplo\n"
    + "INPUT:\n"
    + "[(123, 34924, 'usuario1', 'ola, hoy vi a Baloian', None),"
    + "(124, 24587, 'usuario2', 'de vdd? qué bacan! lo amoooo, y como estaba?', 123),"
    + "(125, 34924, 'usuario1', 'se veía piola, estaba tomando pap', None),"
    + "(126, 24587, 'usuario2', 'ogh que paja, me carga la pap', None),"
    + "(127, 87562, 'usuario3', 'wena cabros descubrí un framework de js se llama TupJS', None),"
    + "(128, 24587, 'usuario2', 'uuu si lo cacho, apaña caleta pero me gusta más BebJS', 127),"
    + "(129, 34924, 'usuario1', 'que chucha están hablando', None)]"
    + "OUTPUT:\n"
    + "<b>Baloian estaba tomando pap</b>\n"
    + "- usuario1 lo vio.\n"
    + "- usuario2 ama a Baloian pero odia la pap.\n"
    + "<b>Conversación sobre frameworks de JS</b>\n"
    + "- usuario3 descubre TupJS.\n"
    + "- usuario2 prefiere BebJS.\n"
    + "- usuario1 no entiende del tema.\n"
)


@command(group_exclusive=True)
def resumir(update: Update, context: CallbackContext, command: Command) -> None:
    """
    Summarizes multiples messages from the database.
    """
    cmd = command
    msg = update.message
    cmd.use_default_opt("prompt")

    ai_model = cmd.opts.get("m") or cmd.opts.get("model") or RESUMIR_MODEL

    client = ai_client(model=ai_model, update=update)
    # Summarize a specific single replied message
    if not cmd.arg and msg.reply_to_message:
        alias_dict = get_alias_dict_from_string(msg.reply_to_message.text)
        prompt_text = anonymize([msg.reply_to_message.text], alias_dict)[0]
        cmd.opts.pop("m", None) and cmd.opts.pop("model", None)
        response = client.generate(
            system=PROMPT_SYSTEM_MESSAGE_SINGLE,
            conversation=[GenAIMessage("user", prompt_text)],
            **cmd.opts,
        )
        result = deanonymize(response.message, alias_dict)
        message_link = f"https://t.me/c/{str(msg.chat_id).replace('-100','')}/{msg.reply_to_message.message_id}"
        # Given that the result can break different parsers, we try to send it in different formats.
        # TODO: Better way to handle this
        try:
            try_msg(
                context.bot,
                chat_id=msg.chat_id,
                parse_mode="HTML",
                text=f'Resumen del <a href="{message_link}">mensaje</a>:\n\n{result}',
                reply_to_message_id=msg.message_id,
            )
        except Exception:
            try:
                try_msg(
                    context.bot,
                    chat_id=msg.chat_id,
                    parse_mode="Markdown",
                    text=f"Resumen del [mensaje]({message_link}):\n\n{result}",
                    reply_to_message_id=msg.message_id,
                )
            except Exception:
                try_msg(
                    context.bot,
                    chat_id=msg.chat_id,
                    text=f"Resumen del mensaje:\n\n{result}",
                    reply_to_message_id=msg.message_id,
                )
        return

    # Summarize N messages
    n = None
    try:
        n = int(cmd.arg)
    except (ValueError, TypeError):
        try_msg(
            context.bot,
            chat_id=msg.chat_id,
            text="Debes indicar la cantidad de mensajes hacia atrás que quieres resumir.",
            reply_to_message_id=msg.message_id,
        )
        return

    if n and n > MAX_MESSAGES_TO_SUMMARIZE:
        try_msg(
            context.bot,
            chat_id=msg.chat_id,
            text=f"El máximo de mensajes a resumir es de {MAX_MESSAGES_TO_SUMMARIZE}.",
            reply_to_message_id=msg.message_id,
        )
        return

    summarize_from = msg.message_id - 1
    if msg.reply_to_message:
        summarize_from = msg.reply_to_message.message_id

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
            chat_id=msg.chat_id,
            text="No hay mensajes para resumir. Es posible que lo que intentas resumir no haya sido registrado en la base de datos.",
            reply_to_message_id=msg.message_id,
        )
        return

    prompt_messages = [
        PROMPT_SYSTEM_MESSAGE_MULTIPLE,
        {
            "role": "user",
            "content": [{"type": "text", "text": str(input_messages)}],
        },
    ]

    input_tokens = num_tokens_from_string(str(prompt_messages), RESUMIR_MODEL)
    expected_output_tokens = 300
    # Based on real usage data
    expected_output_tokens = -300 + 86.8 * math.log(input_tokens + 31.697)

    try_msg(
        context.bot,
        chat_id=msg.chat_id,
        parse_mode="HTML",
        reply_to_message_id=msg.message_id,
        text=f"El resumen de {len(input_messages)} mensajes con <i>{client.model}</i> costará aproximadamente <b>${round(prc.get_total_cost(RESUMIR_MODEL, input_tokens, expected_output_tokens), 3)} USD</b>\n"
        + (f"\nOPTS: {json.dumps(cmd.opts, ensure_ascii=False)}" if cmd.opts else ""),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Resumir",
                        callback_data=json.dumps(
                            ["confirm_summary", n, summarize_from]
                        ),
                    ),
                    InlineKeyboardButton(
                        "Cancelar", callback_data=json.dumps(["cancel_summary"])
                    ),
                ],
            ]
        ),
    )


def _do_resumir(query: CallbackQuery, context: CallbackContext) -> None:
    msg = query.message
    try:
        cmd = CallbackQueryCommand(query)
        cmd.use_default_opt("prompt")

        ai_model = (
            cmd.opts.pop("m", None) or cmd.opts.pop("model", None) or RESUMIR_MODEL
        )
        client = ai_client(model=ai_model, query=query)
        query_data = json.loads(query.data)
        n = query_data[1]
        summarize_from = query_data[2]
        if not summarize_from:
            summarize_from = msg.reply_to_message.message_id

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
        alias_dict = get_alias_dict_from_messages_list(input_messages)
        input_messages = anonymize(input_messages, alias_dict)

        response = client.generate(
            system=PROMPT_SYSTEM_MESSAGE_MULTIPLE,
            conversation=[GenAIMessage("user", str(input_messages))],
            **cmd.opts,
        )

        result = deanonymize(response.message, alias_dict)

        start_message_link = f"https://t.me/c/{str(msg.chat_id).replace('-100','')}/{input_messages[0]['message_id']}"
        end_message_link = f"https://t.me/c/{str(msg.chat_id).replace('-100','')}/{input_messages[-1]['message_id']}"

        # Given that the result can break different parsers, we try to send it in different formats.
        # TODO: Better way to handle this
        html_message = (
            f'Resumen de {len(input_messages)} mensajes [<a href="{start_message_link}">Inicio</a> - <a href="{end_message_link}">Fin</a>]:\n'
            + f"<i>Costo: ${round(response.cost, 5)} USD</i>\n\n"
            + str(result)
        )
        markdown_message = (
            f"Resumen de {len(input_messages)} mensajes [Inicio]({start_message_link}) - [Fin]({end_message_link}]:\n"
            + f"_Costo: ${round(response.cost, 5)} USD_\n\n"
            + str(result)
        )
        text_message = (
            f"Resumen de {len(input_messages)} mensajes:\n"
            + f"Costo: ${round(response.cost, 5)} USD\n\n"
            + str(result)
        )
        try:
            try_msg(
                context.bot,
                chat_id=msg.chat_id,
                parse_mode="HTML",
                text=html_message,
                reply_to_message_id=msg.reply_to_message.message_id,
            )
        except Exception:
            try:
                try_msg(
                    context.bot,
                    chat_id=msg.chat_id,
                    parse_mode="Markdown",
                    text=markdown_message,
                    reply_to_message_id=msg.reply_to_message.message_id,
                )
            except Exception:
                try_msg(
                    context.bot,
                    chat_id=msg.chat_id,
                    text=text_message,
                    reply_to_message_id=msg.reply_to_message.message_id,
                )
    except Exception as e:
        try_msg(
            context.bot,
            chat_id=msg.chat_id,
            text=f"Ocurrió un error al procesar el resumen:\n{e}",
            reply_to_message_id=msg.reply_to_message.message_id,
        )
        raise e


def confirm_resumir(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data = json.loads(query.data)
    # Only requesting user can answer
    if query.message.reply_to_message.from_user.id != query.from_user.id:
        query.answer("Solo quien solicitó el resumen puede confirmarlo.")
        return
    else:
        query.answer()
        if query_data[0] == "confirm_summary":
            query.edit_message_text(
                text=f"{query.message.text}\n\nResumen aceptado. Procesando..."
            )
            _do_resumir(query, context)
        elif query_data[0] == "cancel_summary":
            query.edit_message_text(text=f"{query.message.text}\n\nResumen cancelado.")


@command(member_exclusive=True)
def noticia(update: Update, context: CallbackContext, command: Command) -> None:
    """
    Summarizes a news article from Google News headlines.
    """
    cmd = command
    msg = update.message
    if not cmd.arg:
        return
    cmd.use_default_opt("prompt")

    q = urllib.parse.quote_plus(cmd.arg)
    url = f"https://news.google.com/rss/search?hl=es-419&gl=CL&ceid=CL:es-419&q={q}"
    rss = feedparser.parse(url)

    def parse_entries(entries):
        titles = []
        for entry in entries:
            if "<ol><li>" in entry.description:
                headline_regex = r"<a href=\".*?\">(.*?)<\/a>"
                matches = re.findall(
                    headline_regex,
                    entry.description.replace("\n", ""),
                )
                titles.extend(matches)
            else:
                titles.append(entry.title)
        return titles

    titles = parse_entries(rss.entries)[:10]

    PROMPT_NEWS_HEADLINES = (
        "Eres un bot para resumir titulares de noticias. "
        + "Te daré varios titulares recientes y debes intentar inferir qué está pasando, de forma concisa, en no más de 1000 caracteres."
        + "No incluyas nada más que el resumen en tu mensaje. No menciones las fuentes."
    )

    ai_model = cmd.opts.pop("m", None) or cmd.opts.pop("model", None) or QUEPASO_MODEL
    client = ai_client(ai_model, update)

    result = client.generate(
        system=PROMPT_NEWS_HEADLINES,
        conversation=[GenAIMessage("user", "\n".join(titles))],
        **cmd.opts,
    )

    message = result.message + "\n\n" + f"⛲️ <a href='{url}'>Google News</a>"

    try_msg(
        context.bot,
        chat_id=msg.chat_id,
        parse_mode="HTML",
        text=message,
        reply_to_message_id=msg.message_id,
    )
    return
