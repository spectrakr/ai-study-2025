import random
import traceback

from IPython.display import Image, display
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from dataclasses import dataclass


@dataclass
class NodeStyles:
    default: str = (
        "fill:#45C4B0, fill-opacity:0.3, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:bold, line-height:1.2"  # 기본 색상
    )
    first: str = (
        "fill:#45C4B0, fill-opacity:0.1, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2"  # 점선 테두리
    )
    last: str = (
        "fill:#45C4B0, fill-opacity:1, color:#000000, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2"  # 점선 테두리
    )


# 오프라인 실행이 필요하면 아래 명령어를 실행한다.
# sudo npm install -g @mermaid-js/mermaid-cli
def visualize_graph(graph, xray=False):
    try:
        # 그래프 시각화
        if isinstance(graph, CompiledStateGraph):
            display(
                Image(
                    graph.get_graph(xray=xray).draw_mermaid_png(
                        background_color="white",
                        node_colors=NodeStyles(),
                    )
                )
            )
    except Exception as e:
        print(f"[ERROR] Visualize Graph Error: {e}")


def generate_random_hash():
    return f"{random.randint(0, 0xffffff):06x}"


def extract_action_values(value):
    action_values = []
    for sub_value in value.values():
        if isinstance(sub_value, list):
            for item in sub_value:
                if isinstance(item, tuple):
                    for element in item:
                        action_values.append(f"- {element}")
                elif isinstance(item, AIMessage) and item.tool_calls:
                    tool_call = item.tool_calls[0]["args"]
                    action_values.append(f"- {tool_call}")
                else:
                    action_values.append(f"- {item}")
        else:
            action_values.append(sub_value)

    return action_values


def stream_graph_with_streamlit(
    graph: CompiledStateGraph,
    inputs: dict,
    config: RunnableConfig,
    streamlit_container=None,
    actions_title=None,
    print_actions=None,
):
    if actions_title is None:
        actions_title = {}
    if print_actions is None:
        print_actions = []
    with streamlit_container.status("😊 정보 조회 중...", expanded=True) as status:
        # st.write("계획을 세우는 중입니다.")
        for output in graph.stream(inputs, config=config):
            for key, value in output.items():
                print(f"========== {key} ==========")
                print(f"{value}")
                print("==============================")

                action_values = extract_action_values(value)

                action_values_str = ",".join(
                    f"<span style='font-size:9pt'>{value}</span>"
                    for value in action_values
                )

                if key in print_actions:
                    st.write(f"{actions_title[key]}")
                    st.html(action_values_str)

        status.update(label="조회 완료", state="complete", expanded=False)

    return graph.get_state(config=config).values
