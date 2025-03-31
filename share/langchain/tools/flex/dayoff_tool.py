import requests
from langchain.tools import tool


@tool
def search_dayoff(start_date: str, end_date: str) -> str:
    """
    특정 날짜의 휴가 일정을 조회합니다.

    Args:
        start_date (str): 시작일, YYYY-MM-DD 형식의 날짜 (예: 2024-01-01)
        end_date (str): 종료일, YYYY-MM-DD 형식의 날짜 (예: 2024-01-01)

    Returns:
        str: 해당 날짜의 휴가 일정 정보
    """
    try:
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
