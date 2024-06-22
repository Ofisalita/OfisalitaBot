import data

from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import member_exclusive
from config.logger import log_command
from utils import send_long_message, try_msg


@member_exclusive
def stats(update: Update, context: CallbackContext) -> None:
    """
    Sends a message with the number of tokens used by user.
    """
    log_command(update)
    try:
        usage = data.AIRequests.get()
        for r in usage:
            print(dict(r))

        usage_map = {}
        for r in usage:
            if r["model"] not in usage_map:
                usage_map[r["model"]] = {}
            if r["user_id"] not in usage_map[r["model"]]:
                usage_map[r["model"]][r["user_id"]] = {
                    "input": 0,
                    "output": 0,
                    "cost": 0,
                }
            usage_map[r["model"]][r["user_id"]]["input"] += r["input_tokens"]
            usage_map[r["model"]][r["user_id"]]["output"] += r["output_tokens"]
            usage_map[r["model"]][r["user_id"]]["cost"] += r["cost"]
            usage_map[r["model"]] = dict(
                sorted(
                    usage_map[r["model"]].items(),
                    key=lambda item: item[1]["cost"],
                    reverse=True,
                )
            )

        text = "<b>Estadísticas de uso de tokens:</b>\n"
        for model, users in usage_map.items():
            text += f"\n✨ Modelo: <i>{model}</i> ✨\n"
            for user_id, usage in users.items():
                text += (
                    f"👤 Usuario {user_id}:\n"
                    + f"Input: {usage['input']}; Output: {usage['output']}\n"
                    + f"Gasto: ${round(usage['cost'], 5)} USD\n"
                )
            text += "\n"
            model_total_input = sum([u["input"] for u in users.values()])
            model_total_output = sum([u["output"] for u in users.values()])
            model_total_cost = sum([u["cost"] for u in users.values()])
            text += (
                f"Total input: {model_total_input}; Total output: {model_total_output}\n"
                + f"Gasto total: ${round(model_total_cost, 5)} USD\n"
            )

        send_long_message(
            context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=text,
            reply_to_message_id=update.message.message_id,
        )

    except Exception as e:
        try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            text=f"Hubo un error al obtener las estadísticas: {e}",
            reply_to_message_id=update.message.message_id,
        )
        raise e
