import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("경태의 ChatGPT :sunglasses: 😀 🤗")

with st.sidebar:
    btn_reset = st.button("대화 초기화")

    selected_model = st.selectbox(
        "GPT 모델",
        ("gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"),
        index=0,
        placeholder="모델 선택...",
    )

    system_prompt = st.selectbox(
        "System Prompt",
        (
            "당신은 엄청 불친절한 AI Assistant 입니다.",
            "당신은 친절한 AI Assistant 입니다.",
        ),
        index=0,
        placeholder="프롬프트 선택",
    )

user_input = st.chat_input("궁금한 점을 물어보세요~")


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


if btn_reset:
    st.session_state["messages"] = []

print_messages()


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


if user_input:
    st.chat_message("user").write(user_input)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "#question\n{question}"),
        ]
    )

    llm = ChatOpenAI(model_name=selected_model, temperature=0)
    output_parser = StrOutputParser()

    # chain
    chain = prompt | llm | output_parser
    ai_answer = chain.stream({"question": user_input})

    # st.chat_message("assistant").write(ai_answer)
    with st.chat_message("assistant"):
        container = st.empty()
        answer = ""
        for token in ai_answer:
            answer += token
            container.write(answer)

    add_message(role="user", message=user_input)
    add_message(role="assistant", message=answer)
