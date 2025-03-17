import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

### pip install gradio
### 실행: python main_gradio.py


class ChatbotApp:
    def __init__(self):
        self.messages = []
        self.system_prompt = "당신은 화가난 AI Assistant 입니다."
        self.selected_model = "gpt-4o-mini"

    def reset_conversation(self):
        self.messages = []
        return "", self.messages

    def update_system_prompt(self, prompt):
        self.system_prompt = prompt
        return f"시스템 프롬프트가 업데이트 되었습니다: {prompt}"

    def update_model(self, model):
        self.selected_model = model
        return f"모델이 변경되었습니다: {model}"

    def respond(self, message, chat_history):
        if not message:
            return "", chat_history

        chat_history.append((message, ""))

        prompt = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "#question\n{question}")]
        )

        llm = ChatOpenAI(model_name=self.selected_model, temperature=0, streaming=True)
        chain = prompt | llm | StrOutputParser()

        response = ""
        for chunk in chain.stream({"question": message}):
            response += chunk
            chat_history[-1] = (message, response)
            yield "", chat_history


def create_demo():
    chatbot = ChatbotApp()

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# YJNOH ChatGPT🥳")

        with gr.Row():
            with gr.Column(scale=4):
                chatbot_component = gr.Chatbot(
                    [],
                    height=600,
                    show_label=False,
                )
                msg = gr.Textbox(placeholder="궁금한 것을 입력하세요", show_label=False)

            with gr.Column(scale=1):
                model_dropdown = gr.Dropdown(
                    choices=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                    value="gpt-4o-mini",
                    label="GPT 모델",
                )
                system_prompt_input = gr.Textbox(
                    value=chatbot.system_prompt, label="System Prompt 입력"
                )
                clear = gr.Button("대화 초기화")

        msg.submit(chatbot.respond, [msg, chatbot_component], [msg, chatbot_component])
        clear.click(chatbot.reset_conversation, None, [msg, chatbot_component])
        system_prompt_input.change(
            chatbot.update_system_prompt, system_prompt_input, None
        )
        model_dropdown.change(chatbot.update_model, model_dropdown, None)

    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.queue()
    demo.launch()
