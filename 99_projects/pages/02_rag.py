import os
import sys

import streamlit as st
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from langchain.retrievers import EnsembleRetriever
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def load_path():
    project = "ai-study-2025"
    file_path = os.path.dirname(__file__)
    load_sys_path = file_path[: file_path.rfind(project) + len(project)]
    sys.path.append(load_sys_path)


load_path()

from share.langchain.retriever.custom_elastic_search_bm25 import (
    CustomElasticSearchBM25Retriever,
)

load_dotenv()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("프로야구 리그규정 RAG :sunglasses:")

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
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


def format_docs(docs):
    # formatted_docs = "\n\n".join([f"{doc.page_content}" for doc in docs])
    # list comprehension 구문
    print(f"======= 검색결과: {len(docs)}건 =======")
    formatted_docs = "\n\n".join(
        [
            f"<document><content>{doc.page_content}</content><source>{doc.metadata['source']}</source><page>{int(doc.metadata['page'])+1}</page></document>"
            for doc in docs
        ]
    )

    # print(formatted_docs)

    return formatted_docs


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = ElasticsearchStore(
    es_url="http://172.16.120.203:9201",
    index_name="kmhan_pdf",
    embedding=embeddings,
)
vector_retriever = vector_store.as_retriever(search_kwargs={"k": 3})

elasticsearch_client = Elasticsearch(hosts=["http://172.16.120.203:9201"])
bm25_retriever = CustomElasticSearchBM25Retriever(
    client=elasticsearch_client, index_name="kmhan_pdf", k=3
)

retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5],
)


if user_input:
    st.chat_message("user").write(user_input)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a question-answer AI Assistant."),
            (
                "user",
                """Use the following pieces of the retrieved context to answer th question.
If you don't know the answer, you must say '잘 몰라유~'
Write citation in answer with new line. You must write only filename without filepath.  (ex: 출처: abcdf.pdf)
Answer in KOREAN.

#Question
{question}

#Context
{context}

#answer:""",
            ),
        ]
    )

    llm = ChatOpenAI(model_name=selected_model, temperature=0)
    output_parser = StrOutputParser()

    # chain
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
