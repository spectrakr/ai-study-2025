from typing import List, Dict

from langchain.agents import tool
from langchain_community.tools import TavilySearchResults


@tool
def search_stock_news_from_naver(query: str) -> List[Dict[str, str]]:
    """
    [Naver 금융정보 검색 도구]
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
