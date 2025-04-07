import datetime
import os
import re

from dotenv import load_dotenv
from notion_client import Client


from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notion_post")

# 환경 변수 로드
load_dotenv()


class NotionAutoPoster:
    def __init__(self):
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")

    def create_post(self, title, content: str, category):
        """Notion에 새 페이지 생성"""
        try:

            today = datetime.date.today().isoformat()
            # 페이지 생성
            blocks = self.text_to_notion_blocks(content)
            new_page = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "제목": {"title": [{"text": {"content": title}}]},
                    "카테고리": {"multi_select": [{"name": category}]},
                    "생성 일시": {"date": {"start": today}},
                },
                children=blocks,
            )
            print(f"페이지가 성공적으로 생성되었습니다: {new_page['url']}")
            return True
        except Exception as e:
            print(f"페이지 생성 중 오류 발생: {str(e)}")
            return False

    def get_databases(self):
        return self.notion.databases.list(**{"page_size": 10})

    def text_to_notion_blocks(self, text):
        """텍스트를 Notion 블록으로 직접 변환"""
        blocks = []

        # 마크다운 링크 패턴을 찾아 처리
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        # 텍스트를 줄 단위로 분리
        lines = text.split("\n")

        current_block = None
        current_content = []
        in_code_block = False
        code_language = "plain text"

        for i, line in enumerate(lines):
            # 코드 블록 시작/종료 확인
            if line.strip().startswith("```"):
                if not in_code_block:
                    # 코드 블록 시작
                    in_code_block = True
                    # 언어 확인 (예: ```python)
                    lang_part = line.strip()[3:].strip()
                    if lang_part:
                        code_language = lang_part
                    continue
                else:
                    # 코드 블록 종료
                    in_code_block = False
                    # 코드 블록 추가
                    blocks.append(
                        {
                            "object": "block",
                            "type": "code",
                            "code": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {"content": "\n".join(current_content)},
                                    }
                                ],
                                "language": code_language,
                            },
                        }
                    )
                    current_content = []
                    continue

            # 코드 블록 내부 처리
            if in_code_block:
                current_content.append(line)
                continue

            # 헤딩 처리
            if line.strip().startswith("# "):
                # 이전 블록이 있으면 추가
                if current_block:
                    blocks.append(current_block)

                # 새 헤딩 블록 생성
                current_block = {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line.strip()[2:].strip()},
                            }
                        ]
                    },
                }
                current_content = []
                continue
            elif line.strip().startswith("## "):
                # 이전 블록이 있으면 추가
                if current_block:
                    blocks.append(current_block)

                # 새 헤딩 블록 생성
                current_block = {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line.strip()[3:].strip()},
                            }
                        ]
                    },
                }
                current_content = []
                continue

            # 목록 항목 처리
            if line.strip().startswith("- "):
                # 이전 블록이 있으면 추가
                if current_block:
                    blocks.append(current_block)

                # 새 목록 항목 블록 생성
                current_block = {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line.strip()[2:].strip()},
                            }
                        ]
                    },
                }
                current_content = []
                continue
            elif line.strip().startswith("1. "):
                # 이전 블록이 있으면 추가
                if current_block:
                    blocks.append(current_block)

                # 새 번호 목록 항목 블록 생성
                current_block = {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line.strip()[3:].strip()},
                            }
                        ]
                    },
                }
                current_content = []
                continue

            # 빈 줄 처리 (단락 구분)
            if not line.strip():
                if current_content:
                    # 이전 블록이 있으면 추가
                    if current_block:
                        blocks.append(current_block)

                    # 새 단락 블록 생성
                    current_block = {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": "\n".join(current_content)},
                                }
                            ]
                        },
                    }
                    blocks.append(current_block)
                    current_content = []
                continue

            # 일반 텍스트 처리
            current_content.append(line)

        # 마지막 블록 처리
        if current_content:
            # 이전 블록이 있으면 추가
            if current_block:
                blocks.append(current_block)

            # 새 단락 블록 생성
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "\n".join(current_content)},
                            }
                        ]
                    },
                }
            )

        # 중복 제거 및 정리
        cleaned_blocks = []
        seen_content = set()

        for block in blocks:
            # 블록 내용 추출
            content = ""
            if block["type"] == "paragraph":
                content = block["paragraph"]["rich_text"][0]["text"]["content"]
            elif block["type"] == "heading_1":
                content = block["heading_1"]["rich_text"][0]["text"]["content"]
            elif block["type"] == "heading_2":
                content = block["heading_2"]["rich_text"][0]["text"]["content"]
            elif block["type"] == "bulleted_list_item":
                content = block["bulleted_list_item"]["rich_text"][0]["text"]["content"]
            elif block["type"] == "numbered_list_item":
                content = block["numbered_list_item"]["rich_text"][0]["text"]["content"]
            elif block["type"] == "code":
                content = block["code"]["rich_text"][0]["text"]["content"]

            # 중복되지 않은 내용만 추가
            if content not in seen_content:
                seen_content.add(content)
                cleaned_blocks.append(block)

        # 링크 처리
        processed_blocks = []
        for block in cleaned_blocks:
            if block["type"] == "paragraph":
                # 단락 내 링크 처리
                text = block["paragraph"]["rich_text"][0]["text"]["content"]

                # 링크가 있는지 확인
                if re.search(link_pattern, text):
                    rich_text = []

                    # 링크 패턴 찾기
                    last_end = 0
                    for match in re.finditer(link_pattern, text):
                        # 링크 앞의 텍스트 추가
                        if match.start() > last_end:
                            rich_text.append(
                                {
                                    "type": "text",
                                    "text": {"content": text[last_end : match.start()]},
                                    "annotations": {
                                        "bold": False,
                                        "italic": False,
                                        "strikethrough": False,
                                        "underline": False,
                                        "code": False,
                                        "color": "default",
                                    },
                                }
                            )

                        # 링크 추가
                        link_text = match.group(1)
                        link_url = match.group(2)
                        rich_text.append(
                            {
                                "type": "text",
                                "text": {"content": link_text},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                                "href": link_url,
                            }
                        )

                        last_end = match.end()

                    # 링크 뒤의 텍스트 추가
                    if last_end < len(text):
                        rich_text.append(
                            {
                                "type": "text",
                                "text": {"content": text[last_end:]},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                            }
                        )

                    # 처리된 블록 추가
                    processed_blocks.append(
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": rich_text},
                        }
                    )
                else:
                    # 링크가 없는 경우 원래 블록 그대로 추가
                    processed_blocks.append(block)
            else:
                # 다른 블록 타입은 그대로 추가
                processed_blocks.append(block)

        return processed_blocks


def run_server(transport: str = "stdio"):
    """MCP 서버를 실행합니다.

    Args:
        transport: 통신 방식 ("stdio" 또는 "sse")
    """
    mcp.run(transport=transport)


@mcp.tool()
def post_notion(title: str, content: str, category: str):
    """

    :param title: post 할 제목
    :param content: content
    :param category: category
    :return:
    """
    notion_poster = NotionAutoPoster()
    notion_poster.create_post(title, content, category)

    return f"{title} 등록 성공"


if __name__ == "__main__":
    # post_notion("test", "test", "tes")
    run_server(transport="stdio")
