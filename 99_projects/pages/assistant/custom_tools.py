from datetime import datetime
from typing import List, Dict

from langchain.agents import tool
from langchain_community.tools import ShellTool, TavilySearchResults
from langchain_experimental.tools import PythonREPLTool
from langchain_teddynote.tools import TavilySearch

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


@tool
def search_stock_news(query: str) -> List[Dict[str, str]]:
    """
    주식과 금융에 대한 정보를 검색한다.
    증권, 국내증시, 해외증시, 시장지표, 리서니, 뉴스 기사를 검색한다.
    TOP 종목 조회, 환율, 유가, 금리, 금, 원재재가격 정보를 검색한다.



    """
    tavily_search = TavilySearchResults(
        max_results=6,
        include_answer=True,
        include_raw_content=True,
        include_domains=["https://finance.naver.com"],
    )

    return tavily_search.invoke({"query": query})
