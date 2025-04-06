from dotenv import load_dotenv
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain.memory import ConversationBufferMemory
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

server_params = StdioServerParameters(
    command="python",
    args=[
        "/Users/macbookpro/_WORK/_GIT/ai-study-2025/07_MCP/01_server/python/spectra_dayoff/spectra_dayoff.py"
    ],
)

# 메모리 초기화
memory = ConversationBufferMemory(return_messages=True)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            # 휴가 정보 체인
            vacation_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "당신은 휴가 정보를 조회하는 도우미입니다."),
                    ("human", "{input}"),
                ]
            )
            vacation_chain = vacation_prompt | model | StrOutputParser()

            # 날짜 정보 체인
            date_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "당신은 날짜 정보를 분석하는 도우미입니다."),
                    ("human", "오늘 날짜에 대해 설명해주세요: {input}"),
                ]
            )
            date_chain = date_prompt | model | StrOutputParser()

            # 병렬 체인 구성
            combined_chain = RunnableParallel(
                vacation_info=vacation_chain, date_analysis=date_chain
            )

            # 실행
            query = "오늘 휴가자는?"
            response = await combined_chain.ainvoke({"input": query})

            # 메모리에 대화 저장
            memory.save_context({"input": query}, {"output": str(response)})

            print("\n=== 응답 결과 ===")
            print("휴가 정보:", response["vacation_info"])
            print("날짜 분석:", response["date_analysis"])
            print("\n=== 대화 기록 ===")
            print(memory.load_memory_variables({}))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
