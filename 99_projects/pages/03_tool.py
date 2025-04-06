import os
import queue
import sys
from typing import Any

from langchain.agents import create_tool_calling_agent, AgentExecutor
from streamlit import chat_message

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
)


sys.path.append(project_root)

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

from pages.assistant.custom_tools import (
    get_current_date,
    open_slack,
    search_food,
    search_chinese_food,
    search_stock_news,
)


load_dotenv()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("Tool을 사용하는 AI")

with st.sidebar:
    btn_reset = st.button("대화 초기화")

    selected_model = st.selectbox(
        "GPT 모델",
        ("gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"),
        index=0,
        placeholder="모델 선택 ...",
    )

user_input = st.chat_input("궁금한 점을 물어 보세요~")


def print_message():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


if btn_reset:
    st.session_state["messages"] = []

print_message()


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.queue = queue.Queue()
        self.stop_signal = False

    def on_llm_new_token(self, token: str, **kwaggs) -> None:
        self.queue.put(token)
        self.text += token
        self.container.markdown(self.text)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        self.stop_signal = True


if user_input:
    st.chat_message("user").write(user_input)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are very powerful assistant, but don't know current events.
                You can help with:
                - Getting current date and time
                - Opening applications (Slack)
                """,
            ),
            (
                "user",
                "{input}",
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    chat_message = st.chat_message("assistant")
    stream_container = chat_message.empty()
    stream_handler = StreamHandler(stream_container)

    llm = ChatOpenAI(
        model_name=selected_model,
        temperature=0,
        streaming=True,
        callbacks=[stream_handler],
    )
    output_parser = StrOutputParser()
    tools = [
        get_current_date,
        open_slack,
        search_food,
        search_chinese_food,
        search_stock_news,
    ]

    agent = create_tool_calling_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        callbacks=[stream_handler],
    )

    ai_answer = agent_executor.invoke({"input": user_input})["output"]
    add_message(role="user", message=user_input)
    add_message(role="assistant", message=ai_answer)
