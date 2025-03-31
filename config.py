from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


class ChatConfig:

    @staticmethod
    def get_model_options():
        return ["gpt-4o", "gpt-3.5-turbo", "qwen2.5", "eeve-korean"]

    @staticmethod
    def get_llm(selected_model: str):
        return (
            ChatOllama(model=selected_model, temperature=0.7)
            if selected_model == "qwen2.5" or selected_model == "eeve-korean"
            else ChatOpenAI(model_name=selected_model, temperature=0, streaming=True)
        )

    @staticmethod
    def get_prompt_options():
        return [
            "당신은 도움이 되는 AI 어시스턴트입니다.",
            "당신은 전문적인 프로그래머입니다.",
            "당신은 친근한 대화 상대입니다.",
        ]

    @staticmethod
    def get_rag_prompt(selected_prompt):
        return ChatPromptTemplate.from_messages(
            [
                ("system", selected_prompt),
                (
                    "user",
                    """Use the following pieces of the retrieved context to answer th question.
    If you don't know the answer, you must say '잘 몰라유~'
    Write citation in answer with new line. You must write only filename without filepath and docs page (ex: 출처: abcdf.pdf  1 페이지)
    Answer in KOREAN.
    
    #Question
    {question}
    
    #Context
    {context}
    
    #answer:""",
                ),
            ]
        )
