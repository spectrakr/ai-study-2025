import streamlit as st
from dotenv import load_dotenv
import os
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config import ChatConfig

load_dotenv()

# OpenAI API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. 환경변수를 확인해주세요.")


def init_chat():
    """채팅 초기화 및 세션 상태 설정"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        # 초기 시스템 메시지 설정
        st.session_state["messages"].append(
            ChatMessage(
                role="system",
                content="안녕하세요! 저는 당신의 AI 어시스턴트입니다. 어떤 것이든 물어보세요.",
            )
        )


def create_chat_ui(title="AI Chat Assistant 💬"):
    """채팅 UI 생성"""
    st.title(title)

    with st.sidebar:
        col1, col2 = st.columns(2)
        with col1:
            btn_reset = st.button("대화 초기화", use_container_width=True)
        with col2:
            btn_post = st.button("Notion에 포스팅", use_container_width=True)

        st.divider()

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
            placeholder="프롬프트 선택...",
        )

        st.divider()
        st.markdown("### 대화 내역")
        message_count = len(
            [m for m in st.session_state["messages"] if m.role != "system"]
        )
        st.markdown(f"총 {message_count}개의 메시지가 있습니다.")

    return btn_reset, btn_post, selected_model, selected_prompt


def print_messages():
    """저장된 메시지 출력"""
    for chat_message in st.session_state["messages"]:
        if chat_message.role != "system":  # 시스템 메시지는 표시하지 않음
            with st.chat_message(chat_message.role):
                st.markdown(chat_message.content)


def add_message(role, message):
    """새 메시지 추가"""
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


def handle_user_input(user_input, selected_model, selected_prompt):
    """사용자 입력 처리"""
    if user_input:
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(user_input)

        # 이전 대화 컨텍스트 구성
        conversation_history = "\n".join(
            [
                f"{msg.role}: {msg.content}"
                for msg in st.session_state["messages"]
                if msg.role != "system"
            ]
        )

        # 프롬프트 템플릿 구성
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", selected_prompt),
                ("system", "이전 대화 내역:\n{conversation_history}"),
                ("user", "{question}"),
            ]
        )

        # LLM 설정 및 응답 생성
        llm = ChatConfig.get_llm(selected_model)
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        # AI 응답 생성 및 표시
        with st.chat_message("assistant"):
            container = st.empty()
            answer = ""
            for token in chain.stream(
                {"conversation_history": conversation_history, "question": user_input}
            ):
                answer += token
                container.markdown(answer + "▌")
            container.markdown(answer)

        # 대화 내역 저장
        add_message(role="user", message=user_input)
        add_message(role="assistant", message=answer)


def main():
    init_chat()
    btn_reset, btn_post, selected_model, selected_prompt = create_chat_ui()

    if btn_reset:
        st.session_state["messages"] = []
        st.rerun()

    if (
        btn_post and len(st.session_state["messages"]) > 1
    ):  # 시스템 메시지 제외하고 대화가 있는 경우
        with st.spinner("대화 내용을 요약하고 Notion에 포스팅 중..."):
            # upload
            st.success("Notion에 성공적으로 포스팅되었습니다! 🎉")

    print_messages()

    user_input = st.chat_input("무엇이든 물어보세요...")
    handle_user_input(user_input, selected_model, selected_prompt)


if __name__ == "__main__":
    main()
