from mcp.server.fastmcp import FastMCP

mcp = FastMCP("spectra-dayoff")

@mcp.tool()
async def get_current_date(date: str) -> str:
    """현재 날짜를 가져온다.
    
    Returns:
        str: YYYY-MM-DD 형식의 현재 날짜
    """
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    return current_date


@mcp.tool()
async def get_dayoff(start_date: str, end_date: str) -> str:
    """연차, 휴가를 조회한다.

    Args:
        start_date: 시작 날짜 (ex: 2025-04-01)
        end_date: 종료 날짜 (ex: 2025-04-01)
    """

    return "서정현: 연차 (2025-04-01)"

if __name__ == "__main__":
    # mcp.run(transport='stdio')
    mcp.run(transport='sse')

