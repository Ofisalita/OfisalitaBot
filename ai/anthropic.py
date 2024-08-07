from anthropic import Anthropic
from time import time

from ai.base import AbstractGenAIClient, GenAIResponse, GenAIMessage

try:
    from config.auth import claude_key
except ImportError:
    claude_key = None


class ClaudeClient(AbstractGenAIClient):
    def create_client(self):
        self.api_key = claude_key
        if self.api_key is None or self.api_key == "":
            raise ValueError("Claude API key not found.")
        return Anthropic(api_key=self.api_key)

    def generate(
        self, conversation: list[GenAIMessage], system: str = "", **kwargs
    ) -> GenAIResponse:
        parsed_kwargs = {
            k: (
                float(v)
                if k
                in [
                    "frequency_penalty",
                    "top_logprobs",
                    "max_tokens",
                    "n",
                    "presence_penalty",
                    "seed",
                    "temperature",
                    "top_p",
                ]
                else v
            )
            for k, v in kwargs.items()
        }
        max_tokens = parsed_kwargs.pop("max_tokens", 4096)
        request = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[msg.to_dict() for msg in conversation],
            **parsed_kwargs
        )
        response = self.parse_response(request)
        self.save_request(response)
        return response

    def parse_response(self, response: dict) -> GenAIResponse:
        return GenAIResponse(
            id=response.id,
            response=response,
            datetime=int(time()),
            message=response.content[0].text,
            model=response.model,
            usage={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            },
        )
