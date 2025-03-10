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

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


if btn_reset:
    st.session_state["messages"] = []

print_messages()


user_input = st.chat_input("무엇이든 물어보세요~")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state["messages"].append(ChatMessage(role="human", content=user_input))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "당신은 개구쟁이 AI Assistant 입니다."),
            ("user", "#question\n{question}"),
        ]
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.8)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    ai_answer = chain.stream({"question": user_input})

    with st.chat_message("assistant"):
        container = st.empty()
        answer = ""
        for token in ai_answer:
            answer += token
            container.write(answer)

    st.session_state["messages"].append(ChatMessage(role="ai", content=answer))
