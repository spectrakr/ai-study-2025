import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

### 실행: streamlit run main.py

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("YJNOH ChatGPT🥳")
st.markdown(
    """
    <style>
    /* 전체 배경색 */
    .stApp {
        background-color: #ECEFF1;
        color: #37474F;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: #CFD8DC;
        border-right: 3px solid #B0BEC5;
    }

    /* 사이드바 내부 텍스트 색상 */
    [data-testid="stSidebar"] * {
        color: #37474F;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background-color: #607D8B;
        color: white;
        border-radius: 8px;
        padding: 10px 18px;
    }

    /* 버튼 호버 효과 */
    .stButton>button:hover {
        background-color: #546E7A;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    btn_reset = st.button("대화 초기화")

    selected_model = st.selectbox(
        "GPT 모델",
        ("gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"),
        index=0,
        placeholder="모델 선택하기",
    )

    system_prompt = st.text_input(
        "System Prompt 입력", "당신은 화가난 AI Assistant 입니다."
    )

user_input = st.chat_input("궁금한것을 입력하세요")


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

    with st.chat_message("assistant"):
        container = st.empty()
        answer = ""
        for token in ai_answer:
            answer += token
            container.write(answer)

    add_message(role="user", message=user_input)
    add_message(role="assistant", message=answer)
