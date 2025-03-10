from typing import List

import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

# 전역 변수로 메시지 기록 저장
messages: List[ChatMessage] = []


def chat_with_gpt(message: str, model_name: str, history: List[List[str]]) -> tuple:
    """
    GPT와 대화하는 함수
    """
    # 프롬프트 설정
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI Assistant"),
            ("user", "#question: {question}"),
        ]
    )

    # LLM 설정
    llm = ChatOpenAI(model_name=model_name, temperature=0, streaming=True)

    # 체인 설정 - StrOutputParser 제거
    chain = prompt | llm

    # 메시지 저장 및 history 업데이트
    messages.append(ChatMessage(role="user", content=message))
    history = history + [[message, ""]]  # 새로운 리스트 생성

    # 스트리밍 응답 처리
    partial_message = ""
    for chunk in chain.stream({"question": message}):
        if hasattr(chunk, "content"):  # AIMessage 객체 확인
            partial_message += chunk.content
            history[-1][1] = partial_message
            yield history, ""

    # 최종 응답 저장
    messages.append(ChatMessage(role="assistant", content=partial_message))


def reset_chat() -> tuple:
    """
    대화 기록 초기화
    """
    global messages
    messages = []
    return None, []


# Gradio 인터페이스 생성
with gr.Blocks(title="나의 ChatGPT 😎") as demo:
    gr.Markdown("# 나의 ChatGPT 😎")

    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="대화 내용", height=600)
            msg = gr.Textbox(
                label="무엇이던지 물어보슈~~",
                placeholder="메시지를 입력하세요...",
                show_label=True,
            )

        with gr.Column(scale=1):
            model_dropdown = gr.Dropdown(
                choices=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                value="gpt-4o-mini",
                label="GPT 모델",
            )
            clear = gr.Button("대화 초기화")

    # 이벤트 핸들러 설정
    msg.submit(
        chat_with_gpt,
        inputs=[msg, model_dropdown, chatbot],
        outputs=[chatbot, msg],
        queue=True,  # 큐 활성화
    )

    clear.click(reset_chat, outputs=[msg, chatbot])

if __name__ == "__main__":
    demo.launch()
