import random
import traceback
import os
import tempfile
import subprocess

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


# 오프라인 실행이 필요하면 아래 명령어를 실행한다.
# sudo npm install -g @mermaid-js/mermaid-cli
def visualize_graph_local(graph, xray=False, mmdc_path="mmdc"):
    """
    인터넷 연결 없이 로컬에서 mermaid-cli를 사용하여 그래프를 시각화합니다.

    Args:
        graph: 시각화할 그래프 객체
        xray (bool): xray 모드 활성화 여부
        mmdc_path (str): mermaid-cli 실행 파일 경로 (기본값: "mmdc")

    Note:
        사용 전 다음 명령어로 mermaid-cli를 설치해야 합니다:
        sudo npm install -g @mermaid-js/mermaid-cli
    """
    try:
        if not isinstance(graph, CompiledStateGraph):
            print("[ERROR] 지원되지 않는 그래프 유형입니다.")
            return

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(
            suffix=".mmd", delete=False
        ) as mmd_file, tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as png_file:

            mmd_path = mmd_file.name
            png_path = png_file.name

        # 원래 visualize_graph 함수에서 사용하는 방식과 동일하게 그래프 객체를 가져옵니다
        graph_obj = graph.get_graph(xray=xray)

        # NetworkX 그래프를 수동으로 Mermaid 구문으로 변환
        mermaid_content = "flowchart TD\n"

        # 노드 스타일 정의
        node_styles = NodeStyles()

        # 노드 추가
        for node in graph_obj.nodes():
            node_id = (
                str(node)
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .replace(".", "_")
            )
            node_name = str(node)

            # 노드 스타일 결정
            style = node_styles.default

            # 특수 노드 이름으로 처리 (START, END 등)
            if node_name == "START":
                style = node_styles.first
            elif node_name == "END":
                style = node_styles.last

            mermaid_content += f'    {node_id}["{node_name}"]:::custom\n'
            mermaid_content += f"    style {node_id} {style}\n"

        # 엣지 추가
        for source, target in graph_obj.edges():
            source_id = (
                str(source)
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .replace(".", "_")
            )
            target_id = (
                str(target)
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .replace(".", "_")
            )

            # 엣지 레이블 추가 (있는 경우)
            edge_data = graph_obj.get_edge_data(source, target)
            if edge_data and isinstance(edge_data, dict) and "label" in edge_data:
                label = edge_data["label"]
                mermaid_content += f"    {source_id} -->|{label}| {target_id}\n"
            else:
                mermaid_content += f"    {source_id} --> {target_id}\n"

        # 클래스 정의 추가
        mermaid_content += "    classDef custom fill:#45C4B0;\n"

        # 임시 mermaid 파일에 내용 쓰기
        with open(mmd_path, "w") as f:
            f.write(mermaid_content)

        # mmdc 명령어 실행하여 PNG 생성
        subprocess.run(
            [mmdc_path, "-i", mmd_path, "-o", png_path, "-b", "white"], check=True
        )

        # 이미지 표시
        display(Image(filename=png_path))

        # 임시 파일 정리
        os.unlink(mmd_path)
        os.unlink(png_path)

    except Exception as e:
        print(f"[ERROR] Visualize Graph Local Error: {e}")
        traceback.print_exc()


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
