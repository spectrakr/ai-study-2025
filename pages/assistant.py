import os
import queue
import sys
from typing import Any

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from langchain_teddynote.tools import TavilySearch

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from pages.assistant.custom_tools import (
    find_jira_issue,
    get_current_date,
    get_slack_messages,
    open_kakao,
    open_powerpoint,
    open_slack,
    register_jira_issue,
    search_dayoff,
    send_slack_message,
    translate_text,
    get_github_pr,
    code_review,
    post_review_comment,
)

load_dotenv()


tavily_search = TavilySearch(max_results=3)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("나의 비서 :sunglasses:")
st.markdown(
    """내 개인 비서입니다. 시키면 다 해줍니다.

    예시)
    - 현재시간 (예: [현재시간은?])
    - 프로그램 실행 (예: Slack, 파워포인트, 카카오톡 등)
    - 인터넷 검색 (예: 최근 뉴스 알려줘)
    - 휴가자 조회 (예: 오늘 휴가자 누구야?)
    - Jira 이슈 조회 (예: AVGRS-856 이슈 내용 알려줘)
    - Jira 이슈 등록 (예: AVGRS에 AI 스터디 대충 교육준비로 이슈 등록해줘)
    - Slack 채널(ai-study-2025) 메시지 조회 (예: 최근 메시지 내용 알려줘)
    - Slack 채널(ai-study-2025) 메시지 전송 (예: @정현님에게 교육 들어오라고 메시지 보내줘)
    - 번역하기 (예: Write citation in answer with new line 번역해줘)
    - 파이썬 코드 리뷰하기 (예 : 파이썬 코드 리뷰해줘 code... )
    - github pull 주소를 입력받아 code 변경사항을 조회하는 기능 
    - github pull request에 comment를 남기는 기능
    """
)

with st.sidebar:
    btn_reset = st.button("대화 초기화")

    selected_model = st.selectbox(
        "GPT 모델",
        ("gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"),
        index=0,
        placeholder="모델 선택...",
    )


user_input = st.chat_input("궁금한 점을 물어보세요~")


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


if btn_reset:
    st.session_state["messages"] = []

print_messages()


def add_message(role, message):
    if message is None:
        message = ""
    elif not isinstance(message, str):
        message = str(message)
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.queue = queue.Queue()
        self.stop_signal = False

    def on_llm_new_token(self, token: str, **kwargs) -> None:
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
                - Opening applications (Slack, PowerPoint, KakaoTalk)
                - Searching for day off users
                - Fining, Creating Jira issues
                - Searching the internet
                - translate text
                - review python code
                - getting github pull request diff code
                - post github pull request comment
                """,
            ),
            ("user", "{input}"),
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
        tavily_search,
        find_jira_issue,
        get_current_date,
        get_slack_messages,
        open_kakao,
        open_powerpoint,
        open_slack,
        register_jira_issue,
        search_dayoff,
        send_slack_message,
        translate_text,
        get_github_pr,
        code_review,
        post_review_comment,
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
