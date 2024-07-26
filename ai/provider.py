from telegram import Update, CallbackQuery
from typing import Optional

from ai.base import AbstractGenAIClient
from ai.openai import GPTClient
from ai.anthropic import ClaudeClient

SUPPORTED_MODELS = {
    "openai": {
        "client": GPTClient,
        "models": [
            "gpt-4o",
            "gpt-4o-2024-05-13",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-instruct",
        ],
    },
    "anthropic": {
        "client": ClaudeClient,
        "models": [
            "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
        ],
    },
}


def ai_client(
    model: str, update: Optional[Update] = None, query: Optional[CallbackQuery] = None
) -> AbstractGenAIClient:
    # Find by specific model name
    # e.g. model = "claude-3-5-sonnet-20240620"
    for _brand in SUPPORTED_MODELS:
        for _model in SUPPORTED_MODELS[_brand]["models"]:
            if model == _model:
                return SUPPORTED_MODELS[_brand]["client"](model, update, query)

    # Find by model brand and get the latest version
    # e.g. model = "claude"
    for _brand in SUPPORTED_MODELS:
        if model == _brand:
            return SUPPORTED_MODELS[_brand]["client"](
                SUPPORTED_MODELS[_brand][0], update, query
            )

    # Find by model name prefix
    # e.g. model = "claude-3-5-sonnet"
    for _brand in SUPPORTED_MODELS:
        for _model in SUPPORTED_MODELS[_brand]["models"]:
            if _model.startswith(model):
                return SUPPORTED_MODELS[_brand]["client"](_model, update, query)

    raise ValueError(f"Model '{model}' not found")
