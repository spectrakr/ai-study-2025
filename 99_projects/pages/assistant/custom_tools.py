from datetime import datetime

import requests
from langchain.agents import tool
from langchain_community.tools import ShellTool
from langchain_experimental.tools import PythonREPLTool

from share.langchain.tools.jira.enomix_jira import EnomixJira
from share.slack.service.slack_message_service import SlackMessageService

python_tool = PythonREPLTool()
shell_tool = ShellTool()
jira = EnomixJira()


@tool
def get_current_date():
    """현재 날짜 시간을 조회합니다."""
    return datetime.now()


@tool
def open_slack(command):
    """Slack(슬랙) 프로그램을 실행하는 도구"""

    shell_tool.run({"commands": ["open -a Slack"]})


@tool
def open_powerpoint(command):
    """파워포인트를 실행하는 도구"""

    shell_tool.run({"commands": ["open -a 'Microsoft PowerPoint'"]})


@tool
def open_kakao(command):
    """카카오톡을 실행하는 도구"""
    shell_tool.run({"commands": ["open -a 'KakaoTalk'"]})


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


@tool
def register_jira_issue(project_key, summary, description):
    """jira 이슈를 등록하는 도구

    Args:
        project_key (str): 프로젝트 키
        summary (str): 이슈의 제목
        description (str): 이슈의 상세 내용
    """

    try:
        response = jira.create_issue(project_key, "10351", summary, description)

        if response["key"] is not None:
            return f"이슈가 성공적으로 등록되었습니다. https://enomix.atlassian.net/browse/{response['key']}"
        else:
            return f"이슈 등록 실패"

    except Exception as e:
        return f"이슈 등록 실패: {e}"


@tool
def find_jira_issue(issue_id):
    """jira 이슈를 조회하는 도구

    Args:
        issue_id (str): 이슈 아이디
    """

    try:
        response = jira.get_issue(issue_id)

        return response
    except Exception as e:
        return f"이슈 조회 실패: {e}"


slack_message_service = SlackMessageService()


@tool
def send_slack_message(channel_id: str = "C08DXE0FJJE", message: str = None):
    # kmhan-public-test: C08KMHWPVHR
    # ai-study-2025: C08DXE0FJJE
    """slack에 메시지를 전송하는 도구

    Args:
        message (str): 메시지 내용. 이름의 경우 "성을 빼고 @이름"과 같이 작성해야 함
    """

    def convert_mentions(msg, members_dict):
        import re

        # @이름 패턴을 찾습니다
        mentions = re.findall(r"@(\w+)", msg)

        # 각 이름에 대해 처리
        for name in mentions:
            # members_dict에서 해당 이름을 가진 사용자의 ID를 찾습니다
            for user_id, full_name in members_dict.items():
                if (
                    isinstance(full_name, str) and name in full_name.split()[-1]
                ):  # 성을 제외한 이름만 비교
                    # @이름을 <@USER_ID> 형식으로 변경
                    msg = msg.replace(f"@{name}", f"<@{user_id}>")
                    break

        return msg

    try:
        # members.txt의 내용을 딕셔너리로 변환 (이미 딕셔너리 형태로 저장되어 있음)
        import ast

        with open("../share/slack/members.txt", "r") as f:
            members = ast.literal_eval(f.read())

        # 멘션을 변환
        converted_message = convert_mentions(message, members)

        result = slack_message_service.send_message(
            channel_id=channel_id, text=converted_message
        )
        print(result)

        return result
    except Exception as e:
        return f"메시지 전송 실패: {e}"


@tool
def get_slack_messages(channel_id: str = "C08DXE0FJJE", limit: int = 10) -> str:
    """Slack 채널의 최근 메시지를 조회하는 도구

    Args:
        channel_id (str): Slack 채널 ID (기본값: C08KMHWPVHR - kmhan-public-test)
        limit (int): 조회할 메시지 개수 (기본값: 10)

    Returns:
        str: 메시지 목록 문자열
    """
    try:
        messages = slack_message_service.get_messages(
            channel_id=channel_id, limit=limit
        )

        if not messages:
            return "메시지가 없습니다."

        result = []
        for msg in messages.messages:
            user = msg.user if hasattr(msg, "user") else "알 수 없음"
            text = msg.text if hasattr(msg, "text") else ""
            ts = msg.ts if hasattr(msg, "ts") else ""

            # 타임스탬프를 한국 시간으로 변환
            from datetime import datetime

            import pytz

            dt = datetime.fromtimestamp(float(ts), tz=pytz.UTC)
            kr_tz = pytz.timezone("Asia/Seoul")
            kr_time = dt.astimezone(kr_tz).strftime("%Y-%m-%d %H:%M:%S")

            result.append(f"[{kr_time}] {user}: {text}")

        return "\n".join(result)

    except Exception as e:
        return f"메시지 조회 실패: {str(e)}"
