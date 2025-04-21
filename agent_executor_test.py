from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time():
    """Use this to get current date or time"""
    return datetime.now()

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

tools = [get_current_time]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm = llm.bind_tools(tools)
prompt = PromptTemplate.from_template("""
You are an AI Assistant

question: {question}

{agent_scratchpad}
""")

def chatbot(state: State):
    agent = create_tool_calling_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=10,
        max_execution_time=10,
        handle_parsing_errors=True,
    )
    user_question = state["messages"][-1]
    result = agent_executor.invoke({"question": user_question})
    ai_answer = result["output"]

    return {"messages": [ai_answer]}
    # return {"messages": [llm.invoke(state["messages"])]}


graph_builder = StateGraph(State)
tool_node = ToolNode(tools=[tool])

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
# 도구 노드 추가
graph_builder.add_node("tools", tool_node)

# 조건부 엣지
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

from langchain_core.messages import HumanMessage

# question = "한국에 대해 100글자로 요약해줘"
question = "현재 시간은?"
inputs = {"messages": [("user", question)], }

# result = graph.stream(inputs, stream_mode="messages")
# for chunk in result:
#     print(chunk)
# print(result)
for chunk_msg, metadata  in graph.stream(inputs, stream_mode="messages"):
    if (
            chunk_msg.content
            and not isinstance(chunk_msg, HumanMessage)
            and metadata["langgraph_node"] == "chatbot"
    ):
        print(chunk_msg.content, end="", flush=True)
