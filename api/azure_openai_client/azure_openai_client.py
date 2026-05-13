import os
from collections.abc import Sequence

from azure.identity import EnvironmentCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AzureOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.create_embedding_response import CreateEmbeddingResponse


class AzureOpenAIClient:
    """Small wrapper around the configured Azure OpenAI SDK client."""

    def __init__(self) -> None:
        load_dotenv(override=True)

        token_provider = get_bearer_token_provider(
            EnvironmentCredential(),
            "https://cognitiveservices.azure.com/.default",
        )

        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_ad_token_provider=token_provider,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        self.gpt_model = os.getenv("AZURE_OPENAI_MODEL_GPT4o")
        self.embedding_model = os.getenv("AZURE_OPENAI_MODEL_ADA2")

    def create_chat_completion(
        self,
        messages: Sequence[ChatCompletionMessageParam],
    ) -> ChatCompletion:
        return self.client.chat.completions.create(
            model=self.gpt_model,
            messages=messages,
        )

    def create_embedding(self, text: str) -> CreateEmbeddingResponse:
        return self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
