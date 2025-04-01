import uuid
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pages.setting.pdf_index_setting import pdf_setting
from projects.elastic.doc.embedded_docs import IndexPromptStore
from projects.elastic.doc.file_neme import FileNameStore
from projects.retriever.pdf_retriever import PdfRetriever
from projects.store.pdf_store import PdfStore
from elastic_client import ElasticClient
from config import ChatConfig
from share.slack.util.logger import setup_logger

load_dotenv()


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "new_index" not in st.session_state:
    st.session_state["new_index"] = "default_pdf_index"
if "new_prompt" not in st.session_state:
    st.session_state["new_prompt"] = "당신은 도움이 되는 AI 어시스턴트입니다."

st.title("RAG :sunglasses:")

pdf_store = PdfStore()
index_prompt_store = IndexPromptStore()
file_name_store = FileNameStore()
logger = setup_logger(__name__)


def generate_filename():
    # 타임스탬프와 UUID를 조합하여 고유한 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # UUID의 처음 8자리만 사용
    return f"doc_{timestamp}_{unique_id}.pdf"


# PDF 업로드 섹션
with st.sidebar:
    index_prompt_list = index_prompt_store.get_all_docs()
    prompt_option = [index_prompt.prompt for index_prompt in index_prompt_list]
    selected_model = st.selectbox(
        "GPT 모델",
        ChatConfig.get_model_options(),
        index=0,
        placeholder="모델 선택...",
    )
    selected_prompt = st.selectbox(
        "System Prompt",
        prompt_option,
        index=0,
        placeholder="모델 선택...",
    )
    btn_reset = st.button("대화 초기화")
    st.subheader("PDF 문서 추가하기")

    # 인덱스 관리
    st.subheader("인덱스 관리")
    new_index_name = st.text_input("저장할 인덱스 이름", key="new_index")
    new_prompt = st.text_area("시스템 프롬프트", key="new_prompt")
    # PDF 업로드
    st.subheader("PDF 업로드")
    uploaded_file = st.file_uploader("PDF 파일 업로드", type="pdf")
    if uploaded_file and new_index_name and new_prompt:
        if st.button("임베딩 시작"):
            with st.spinner("PDF 임베딩 중..."):
                try:
                    # 파일명 생성
                    safe_filename = generate_filename()

                    # data 디렉토리 생성 (절대 경로 사용)
                    workspace_root = Path(__file__).parent.parent
                    data_dir = workspace_root / "projects" / "data"
                    data_dir.mkdir(parents=True, exist_ok=True)

                    # PDF 파일 저장 (절대 경로 사용)
                    file_path = data_dir / safe_filename
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    # 인덱스 생성
                    ElasticClient.create_index(
                        index_name=new_index_name, settings=pdf_setting
                    )

                    # PDF 임베딩 (절대 경로 문자열로 변환)
                    pdf_store.embedding_pdf(new_index_name, str(file_path))

                    # 프롬프트 저장
                    index_prompt_store.add_docs(
                        index_name=new_index_name,
                        prompt=new_prompt,
                        file_name=uploaded_file.name,
                    )

                    file_name_store.add_docs(
                        file_name=safe_filename, real_file_name=uploaded_file.name
                    )

                    st.success(f"PDF 임베딩 완료! (인덱스: {new_index_name})")

                except Exception as e:
                    st.error(f"임베딩 실패: {str(e)}")
                    logger.error(f"PDF 임베딩 실패: {str(e)}")


user_input = st.chat_input("궁금한 점을 물어보세요~")


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


if btn_reset:
    st.session_state["messages"] = []

print_messages()


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


def get_real_file_name(file_name):
    return file_name_store.get_real_name(file_name=file_name)


def format_docs(docs):
    logger.info(f"======= 검색결과: {len(docs)}건 =======")

    formatted_docs = "\n\n".join(
        [
            f"<document><content>{doc.page_content}</content><source>{get_real_file_name(str(doc.metadata['source']).split('/')[-1] )}</source><page>{int(doc.metadata['page'])+1}</page></document>"
            for doc in docs
        ]
    )

    return formatted_docs


if user_input:
    st.chat_message("user").write(user_input)

    llm = ChatConfig.get_llm(selected_model)
    output_parser = StrOutputParser()
    prompt = ChatConfig.get_rag_prompt(selected_prompt)
    # chain
    prompt_idx = prompt_option.index(selected_prompt)
    rag_index = index_prompt_list[prompt_idx].index_name
    retriever = PdfRetriever.ger_ensemble_retriever(
        rag_index, pdf_store.get_retriever(rag_index)
    )
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
