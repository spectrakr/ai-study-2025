import base64
import requests
from IPython.display import Image, display
import os
import time
import json
import base64
import httpx
from enum import Enum

import anthropic
import pandas as pd

from openai import OpenAI
from openai import AssistantEventHandler
from typing_extensions import override

from langchain_core.language_models.chat_models import (
    BaseChatModel,
    generate_from_stream,
)
from typing import Any, Dict, List, Optional, Iterator
from pydantic import Field
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs.chat_generation import ChatGeneration, ChatGenerationChunk
from langchain_core.outputs import ChatResult

########################


class LLMs(Enum):
    GPT4o_MINI = "gpt-4o-mini"
    GPT4o = "gpt-4o"
    GPT4 = GPT4o_MINI

    O1_PREVIEW = "o1-preview"
    O1_MINI = "o1-mini"
    O1 = O1_MINI

    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_HAIKU = "claude-3-5-haiku-20241022"
    CLAUDE = CLAUDE_SONNET

    UPSTAGE_SOLAR_MINI = "solar-mini"
    UPSTAGE_SOLAR_PRO = "solar-pro"
    UPSTAGE = UPSTAGE_SOLAR_PRO


class Embeddings(Enum):
    OPENAI_EMBEDDING_SMALL = "text-embedding-3-small"
    OPENAI_EMBEDDING_LARGE = "text-embedding-3-large"
    OPENAI_EMBEDDING = OPENAI_EMBEDDING_SMALL

    UPSTAGE_EMBEDDING_QUERY = "embedding-query"
    UPSTAGE_EMBEDDING_PASSAGE = "embedding-passage"
    UPSTAGE_EMBEDDING = UPSTAGE_EMBEDDING_PASSAGE


##########


class MultiModal:
    def __init__(self, model, system_prompt=None, user_prompt=None):
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.init_prompt()

    def init_prompt(self):
        if self.system_prompt is None:
            self.system_prompt = "You are a helpful assistant on parsing images."
        if self.user_prompt is None:
            self.user_prompt = "Explain the given images in-depth in KOREAN."

    # 이미지를 base64로 인코딩하는 함수 (URL)
    def encode_image_from_url(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            image_content = response.content
            if url.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif url.lower().endswith(".png"):
                mime_type = "image/png"
            else:
                mime_type = "image/unknown"
            return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"
        else:
            raise Exception("Failed to download image")

    # 이미지를 base64로 인코딩하는 함수 (파일)
    def encode_image_from_file(self, file_path):
        with open(file_path, "rb") as image_file:
            image_content = image_file.read()
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif file_ext == ".png":
                mime_type = "image/png"
            else:
                mime_type = "image/unknown"
            return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"

    # 이미지 경로에 따라 적절한 함수를 호출하는 함수
    def encode_image(self, image_path):
        if image_path.startswith("http://") or image_path.startswith("https://"):
            return self.encode_image_from_url(image_path)
        else:
            return self.encode_image_from_file(image_path)

    def display_image(self, encoded_image):
        display(Image(url=encoded_image))

    def create_messages(
        self, image_url, system_prompt=None, user_prompt=None, display_image=True
    ):
        encoded_image = self.encode_image(image_url)
        if display_image:
            self.display_image(encoded_image)

        system_prompt = (
            system_prompt if system_prompt is not None else self.system_prompt
        )

        user_prompt = user_prompt if user_prompt is not None else self.user_prompt

        # 인코딩된 이미지를 사용하여 다른 처리를 수행할 수 있습니다.
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"{encoded_image}"},
                    },
                ],
            },
        ]
        return messages

    def invoke(
        self, image_url, system_prompt=None, user_prompt=None, display_image=True
    ):
        messages = self.create_messages(
            image_url, system_prompt, user_prompt, display_image
        )
        response = self.model.invoke(messages)
        return response.content

    def batch(
        self,
        image_urls: list[str],
        system_prompts: list[str] = [],
        user_prompts: list[str] = [],
        display_image=False,
    ):
        messages = []
        for image_url, system_prompt, user_prompt in zip(
            image_urls, system_prompts, user_prompts
        ):
            message = self.create_messages(
                image_url, system_prompt, user_prompt, display_image
            )
            messages.append(message)
        response = self.model.batch(messages)
        return [r.content for r in response]

    def stream(
        self, image_url, system_prompt=None, user_prompt=None, display_image=True
    ):
        messages = self.create_messages(
            image_url, system_prompt, user_prompt, display_image
        )
        response = self.model.stream(messages)
        return response


class OpenAIStreamHandler(AssistantEventHandler):
    @override
    def on_text_delta(self, delta, snapshot):
        return delta.value


def get_model_name(model: LLMs | Embeddings) -> str:
    """
    Enum 클래스로부터 모델의 최종 value 값을 추출하여 반환합니다.

    Args:
        model (LLMs | Embeddings): LLMs 또는 Embeddings Enum 클래스

    Returns:
        str: 모델의 최종 value 값. 유효하지 않은 Enum인 경우 None 반환
    """
    try:
        # value가 Enum 멤버인 경우 최종 값을 반환
        current_value = model.value
        while isinstance(current_value, Enum):
            current_value = current_value.value
        return current_value
    except AttributeError:
        return None
