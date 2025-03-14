import streamlit as s
from dotenv import load_dotenv
from gradio import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()


def init():
    s.session_state["messages"] = []


if "messages" not in s.session_state:
    s.session_state["messages"] = []

s.title("")

with s.sidebar:
    btn_reset = s.button("reset")


def get_messages():
    return s.session_state["messages"]


def print_messages():
    for m in get_messages():
        s.chat_message(m.role).write(m.content)


def add_mesasge(role, m):
    s.session_state["messages"].append(ChatMessage(role=role, content=m))


if btn_reset:
    init()

user_input = s.chat_input("write message")

if user_input:
    s.chat_message("user").write(user_input)

    prompt = PromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI Assistant"),
            ("user", "Uor are a helpful AI Assistant"),
        ]
    )
    llm = default_llm = ChatOllama(model="qwen2.5", temperature=0.7)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser
    ai_answer = chain.invoke({"question": user_input})
    s.chat_message("assistant").write(user_input)

    add_mesasge("user", user_input)
    add_mesasge("assistant", ai_answer)
