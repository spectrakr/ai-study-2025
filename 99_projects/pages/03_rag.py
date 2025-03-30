from lib2to3.btm_utils import tokens

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sympy.physics.units import temperature

load_dotenv()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("공매도 재개 증시 영향 보고서 RAG")

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


def format_docs(docs):
    formatted_docs = "\n\n".join(
        [
            f"<document><content>{doc.page_content}</content><source>{doc.metadata['source']}</source><page>{int(doc.metadata['page'])+1}</page></document>"
            for doc in docs
        ]
    )
    print("======= formatted_docs =======")
    print(formatted_docs)

    return formatted_docs


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = ElasticsearchStore(
    es_url="http://172.16.120.203:9201",
    index_name="sylee_pdf",
    # index_name="kmhan_pdf",
    embedding=embeddings,
)

if user_input:
    st.chat_message("user").write(user_input)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a question-answer AI Assistant."),
            (
                "user",
                """
    Use the following pieces of the retrieved context to answer the question.
    If you don't know the answer, you must say '잘 모르겠습니다.'
    Write citation in answer with new line. You must write only filename without filepath. (e.g. 출처:some.pdf)
    Answer in KOREAN.

    #question
    {question}

    #context
    {context}

    #answer:

                 """,
            ),
        ]
    )

    llm = ChatOpenAI(model_name=selected_model, temperature=0)
    output_parser = StrOutputParser()
    retriever = vector_store.as_retriever()

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )

    ai_answer = chain.stream(user_input)

    with st.chat_message("assistant"):
        container = st.empty()
        answer = ""
        for token in ai_answer:
            answer += token
            container.write(answer)
    add_message(role="user", message=user_input)
    add_message(role="assistant", message=answer)
