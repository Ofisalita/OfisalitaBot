from abc import ABC, abstractmethod
from telegram import Update, CallbackQuery
from typing import Optional

from data import AIRequests
from ai.pricing import get_model_pricing, get_total_cost


class GenAIMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class GenAIResponse:
    def __init__(
        self,
        id: str,
        response: dict,
        datetime: str,
        message: str,
        model: str,
        usage: dict[str, int],
    ):
        self.id = id
        self.response = response
        self.datetime = datetime
        self.message = message
        self.model = model
        self.usage = usage
        self.pricing = get_model_pricing(model)
        self.cost = get_total_cost(
            model,
            usage["input"],
            usage["output"],
        )


class AbstractGenAIClient(ABC):
    def __init__(
        self,
        model: str,
        update: Optional[Update] = None,
        query: Optional[CallbackQuery] = None,
    ):
        if update and query or not update and not query:
            raise ValueError("Either 'update' or 'query' must be provided")
        self.model = model
        self.api_key = None
        if update:
            self.user_id = update.effective_user.id
            self.username = update.effective_user.username
        elif query:
            self.user_id = query.message.reply_to_message.from_user.id
            self.username = query.message.reply_to_message.from_user.username
        self.client = self.create_client()

    @abstractmethod
    def create_client(self):
        pass

    @abstractmethod
    def generate(
        self, conversation: list[GenAIMessage], system: str = None, **kwargs
    ) -> GenAIResponse:
        # Remember to call self.save_request(response) after parsing the response
        pass

    @abstractmethod
    def parse_response(self, response) -> GenAIResponse:
        pass

    def save_request(self, response: GenAIResponse):
        AIRequests.add(
            datetime=response.datetime,
            user_id=self.user_id,
            username=self.username,
            model=response.model,
            input_tokens=response.usage["input"],
            output_tokens=response.usage["output"],
            input_price_per_m=response.pricing["input"],
            output_price_per_m=response.pricing["output"],
            cost=response.cost,
        )

    def add_extra_prompt(self, original_prompt: str, opts: dict) -> str:
        extra_prompt = opts.pop("prompt", None) or opts.pop("p", None)
        return original_prompt + (
            f"\nAdemás, considera lo siguiente: {extra_prompt}" if extra_prompt else ""
        )
