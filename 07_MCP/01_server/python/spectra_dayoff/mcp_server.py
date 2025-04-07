import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("spectra-dayoff")


@mcp.tool()
async def get_current_date(date: str) -> str:
    """현재 날짜를 가져온다.

    Returns:
        str: YYYY-MM-DD 형식의 현재 날짜
    """
    from datetime import datetime

    print("get_current_date 호출")
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool()
async def get_dayoff(start_date: str, end_date: str) -> str:
    """연차, 휴가를 조회한다.

    Args:
        start_date: 시작 날짜 (ex: 2025-04-01)
        end_date: 종료 날짜 (ex: 2025-04-01)
    """

    try:
        print("get_dayoff 호출")
        url = "http://172.16.120.203:9201/flex_dayoff_calendar/_search"
        body = {"query": {"range": {"date": {"gte": start_date, "lte": end_date}}}}
        response = requests.post(url, json=body)

        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", {}).get("hits", [])

            if hits:
                result = []
                for hit in hits:
                    source = hit.get("_source", {})
                    result.append(
                        f"[날짜] {source.get('date', '정보 없음')}\n "
                        f"[휴가자] {source.get('text', '정보 없음')}, "
                    )
                return "\n".join(result)
            else:
                return f"해당하는 휴가 일정이 없습니다."
        else:
            return f"API 호출 실패: HTTP {response.status_code}"

    except ValueError:
        return "잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요."
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"


def run_server(transport: str = "stdio"):
    """MCP 서버를 실행합니다.

    Args:
        transport: 통신 방식 ("stdio" 또는 "sse")
    """
    mcp.run(transport=transport)
