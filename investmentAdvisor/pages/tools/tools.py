from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import tool
from langchain_community.tools import TavilySearchResults
import yfinance as yf


@tool
def search_stock_news_from_naver(query: str) -> List[Dict[str, str]]:
    """
    [Naver Finance 금융정보 검색 도구]
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


class StockInfo(BaseModel):
    name: str = Field(description="종목 이름")


@tool
def search_stock_news_from_yahoo(query: str) -> str:
    """
    [Yahoo Finance 종목정보 검색 도구]
    Yahoo Finace에서 종목 정보를 검색하여 리턴한다.

    """

    parser = PydanticOutputParser(pydantic_object=StockInfo)
    prompt = PromptTemplate.from_template(
        """
    You are a helpful assistant. Please answer the following questions.
    
    INSTRUCTION:
    {instruction}
    
    QUERY:
    {query}
    
    FORMAT:
    {format}    
        """
    )
    prompt = prompt.partial(format=parser.get_format_instructions())
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    llm_with_structured = llm.with_structured_output(StockInfo)
    chain = prompt | llm_with_structured
    answer = chain.invoke(
        {
            "query": query,
            "instruction": "종목 이름 추출",
        }
    )

    stock_name = answer.model_dump()["name"]

    print(f"추출된 종목명: {stock_name} ")

    return get_stock_info(stock_name)


def get_stock_info(name_or_ticker: str) -> str:
    """
    [Yahoo Finance 종목정보 검색 도구]
    Yahoo Finace에서 종목 정보를 검색하여 리턴한다.

    """
    stock = yf.Ticker(name_or_ticker)
    hist = stock.history(period="1mo")
    current_price = hist["Close"][-1]

    # RSI 계산
    delta = hist["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi[-1]

    # 쿼리에 현재 가격과 RSI 정보 추가
    stock_info = f"""
        종목: {name_or_ticker}
        현재가: {current_price:.2f}
        RSI: {current_rsi:.2f}
        """
    return stock_info
