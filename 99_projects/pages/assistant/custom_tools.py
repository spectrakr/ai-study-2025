from datetime import datetime
from typing import List, Dict

from langchain.agents import tool
from langchain_community.tools import ShellTool
from langchain_experimental.tools import PythonREPLTool

python_tool = PythonREPLTool()
shell_tool = ShellTool()


@tool
def get_current_date():
    """현재 날짜 시간을 조회합니다."""
    return datetime.now()


@tool
def open_slack(command):
    """Slack(슬랙) 프로그램을 실행하는 도구"""
    shell_tool.run({"commands": ["open -a Slack"]})


@tool
def search_food(query: str) -> List[Dict[str, str]]:
    """메뉴 목록을 조회한다"""
    return "주문할 수 있는 메뉴는 떡뽁기, 순대, 김방, 어묵이 있습니다"


@tool
def search_chinese_food() -> Dict[str, str]:
    """중식 메뉴 목록을 조회한다"""
    return {"자장면": "5000원", "짬뽕": "3000원"}
