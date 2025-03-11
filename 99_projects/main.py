import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

st.title("용진 ChatGPT :grin:")

with st.sidebar:
    btn_reset = st.button("대화 초기화")

    selected_model = st.selectbox(
        "GPT 모델",
        ("gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"),
        index=0,
        placeholder="gpt 모델 선택",
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


if btn_reset:
    st.session_state["messages"] = []
    st.session_state.question = ""

if selected_model != st.session_state.selected_model:
    st.session_state.selected_model = selected_model
    st.session_state["messages"] = []

print_messages()

user_input = st.chat_input("무엇이든 물어보세요~")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))
    st.session_state.question += user_input

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "당신은 AI 전문 개발자 AI Assistant 입니다."),
            ("user", "#question\n{question}"),
        ]
    )

    llm = ChatOpenAI(model_name=selected_model, temperature=0.8)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    ai_answer = chain.stream({"question": st.session_state.question})

    with st.chat_message("assistant"):
        container = st.empty()
        answer = ""
        for token in ai_answer:
            answer += token
            container.write(answer)

    st.session_state["messages"].append(ChatMessage(role="ai", content=answer))
