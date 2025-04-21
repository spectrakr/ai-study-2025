from langchain_core.messages import HumanMessage, AIMessage


def get_role_from_messages(msg):
    if isinstance(msg, HumanMessage):
        return "user"
    elif isinstance(msg, AIMessage):
        return "assistant"
    else:
        return "assistant"

def messages_to_history(messages):
    return "\n".join(
        [f"{get_role_from_messages(msg)}: {msg.content}" for msg in messages]
    )