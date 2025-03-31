import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import ChatConfig

load_dotenv()


def init_chat():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


def create_chat_ui(title="나의 ChatGPT :sunglasses:"):
    st.title(title)

    with st.sidebar:
        btn_reset = st.button("대화 초기화")

        selected_model = st.selectbox(
            "GPT 모델",
            ChatConfig.get_model_options(),
            index=0,
            placeholder="모델 선택...",
        )

        selected_prompt = st.selectbox(
            "System Prompt",
            ChatConfig.get_prompt_options(),
            index=0,
            placeholder="모델 선택...",
        )

    return btn_reset, selected_model, selected_prompt


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


def handle_user_input(user_input, selected_model, selected_prompt):
    if user_input:
        st.chat_message("user").write(user_input)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", selected_prompt),
                ("user", "#question\n{question}"),
            ]
        )
        llm = ChatConfig.get_llm(selected_model)
        output_parser = StrOutputParser()

        # chain
        chain = prompt | llm | output_parser
        ai_answer = chain.stream({"question": user_input})

        with st.chat_message("assistant"):
            container = st.empty()
            answer = ""
            for token in ai_answer:
                answer += token
                container.write(answer)

        add_message(role="user", message=user_input)
        add_message(role="assistant", message=answer)


def main():
    init_chat()
    btn_reset, selected_model, selected_prompt = create_chat_ui()
    user_input = st.chat_input("궁금한 점을 물어보세요~")

    if btn_reset:
        st.session_state["messages"] = []

    print_messages()
    handle_user_input(user_input, selected_model, selected_prompt)


if __name__ == "__main__":
    main()
