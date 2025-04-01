from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()


class CodeReview:
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a code reviewer. Please carefully analyze the given code and check the following points:
                1. Code quality and readability
                2. Potential bugs or errors
                3. Performance improvement points
                4. Compliance with coding conventions
                5. Security vulnerabilities"
                6. filename은 꼭 경로를 포함한 full path로 입력해줘
                """,
            ),
            (
                "user",
                """
                아래 github pull request diff 정보를 활용해 코드 리뷰 해줘
                응답 값에 filename ( 경로를 포함한 path )과 comment는 꼭 추가 해줘
                filename 
                comment
                pull request diff start
                {code}
                pull request diff end
                """,
            ),
        ]
    )

    @classmethod
    def code_review(cls, code):
        output_parser = StrOutputParser()

        # chain
        chain = cls.prompt | cls.llm | output_parser
        return chain.invoke({"code": code})


if __name__ == "__main__":
    service = CodeReview()
    print(
        service.code_review(
            """Use the following pieces of the retrieved context to answer th question.
    If you don't know the answer, you must say '잘 몰라유~'
    Write citation in answer with new line. You must write only filename without filepath and docs page (ex: 출처: abcdf.pdf  1 페이지)
    Answer in KOREAN.
    
"""
        )
    )
