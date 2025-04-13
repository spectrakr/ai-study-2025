import json
import asyncio
import logging
from typing import List, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from langchain_community.tools import TavilySearchResults
from datetime import datetime


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# MCP 서버 초기화
mcp = FastMCP("finance-news-search")


@mcp.tool()
def get_current_date(date: str) -> str:
    """현재 날짜를 가져온다.

    Returns:
            str: YYYY-MM-DD 형식의 현재 날짜
    """
    logger.info("get_current_date 호출")
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool()
def get_current_time() -> str:
    """현재 시간을 가져온다.

    Returns:
            str: YYYY-MM-DD HH:MM:SS 형식의 현재 시간
    """
    logger.info("get_current_time 호출")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
async def search_finance_news(query: str) -> List[Dict]:
    """금융 기사를 검색
    주식과 금융에 대한 정보를 검색한다.
    증권, 국내증시, 해외증시, 시장지표, 리서치, 뉴스 기사를 검색한다.
    TOP 종목 조회, 환율, 유가, 금리, 금, 원재재가격 정보를 검색한다.

    Args:
        query: 검색키워드 e.g. TOP 종목 조회

    Returns:
        List[Dict]: 검색 결과 리스트
    """
    try:
        tavily_search = TavilySearchResults(
            max_results=6,
            include_answer=True,
            include_raw_content=True,
            include_domains=["https://finance.naver.com"],
            search_depth="advanced",
        )

        logger.info(f"query: {query}")
        search_result = await tavily_search.ainvoke({"query": query})
        logger.info(f"search_result: {search_result}")

        if isinstance(search_result, str):
            search_result = json.loads(search_result)

        return search_result
    except Exception as e:
        logger.error(f"Error in search_finance_new: {str(e)}")
        return []


def run_server(transport: str = "stdio"):
    """MCP 서버를 실행합니다.
    Args:
        transport: 통신 방식 ("stdio" 또는 "sse")
    """
    try:
        logger.info(f"서버 실행 시작 (transport: {transport})")
        # 서버 실행
        mcp.run(transport=transport)
    except Exception as e:
        logger.error(f"서버 실행 실패: {str(e)}")
        raise
