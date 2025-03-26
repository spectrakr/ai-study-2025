import os
import sys

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from share.langchain.tools.jira.issue_content_utils import (
    extract_texts,
    format_date_simple,
    get_comments_text,
    get_customfield_values,
)

load_dotenv()


class EnomixJira:
    """
    Enomix Jira API를 활용 (enomix.atlassian.net)
    """

    def __init__(self, debug=False):
        self.base_url = "https://enomix.atlassian.net"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if (
            os.environ.get("JIRA_EMAIL") is None
            or os.environ.get("JIRA_API_TOKEN") is None
        ):
            print(
                "JIRA_EMAIL or JIRA_API_TOKEN is not set. Please set it in .env file."
            )
            sys.exit(1)

        self.auth = HTTPBasicAuth(
            os.environ["JIRA_EMAIL"],
            os.environ["JIRA_API_TOKEN"],
        )
        self.debug = debug
        self.customfields = self.get_customfields()

    def send_request(self, endpoint, method="GET", data=None):
        if method == "GET":
            response = requests.get(endpoint, headers=self.headers, auth=self.auth)
        elif method == "POST":
            response = requests.post(
                endpoint, headers=self.headers, auth=self.auth, json=data
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

        if not str(response.status_code).startswith("2"):  # 200 or 201
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        return response.json()

    def get_project(self, project_key):
        endpoint = f"{self.base_url}/rest/api/3/project/{project_key}"

        data = {}

        try:
            result = self.send_request(endpoint)

            if result is not None:
                # print(f"Request for getting project data has been succeed. \n result : {result}")
                data["project_id"] = result["id"]
                data["project_name"] = result["name"]
                data["assignee_id"] = result["lead"]["accountId"]
                data["assignee_name"] = result["lead"]["displayName"]
            else:
                print(
                    f"Request for getting project data has been failed. Project Key : {project_key}"
                )
        except Exception as e:
            print(str(e))

        return data

    def get_issue_list(self, jql, start_at=0, max_results=10):
        endpoint = f"{self.base_url}/rest/api/3/search"
        keys = []

        # max_results는 jira api에서 100건으로 제한되어 있음
        max_row_count = 100
        rows_count = 100
        start = start_at

        page_no = 1
        while True:
            # print("start:", start, "end:", end, "max_results:", max_results, "page_no:", page_no, "rows_count:", rows_count)
            if rows_count > max_results:
                rows_count = max_results

            if rows_count * page_no > max_results:
                rows_count = max_results % rows_count
            if rows_count == 0:
                break

            jql_query = {"startAt": start, "maxResults": rows_count, "jql": jql}
            print(jql_query)
            if self.debug:
                print(jql_query)
            response = self.send_request(endpoint, method="POST", data=jql_query)

            if response is None or not response["issues"]:
                break

            issues = response["issues"]
            keys.extend([issue["key"] for issue in issues])

            start += rows_count
            page_no += 1

            if rows_count < max_row_count:
                break

        return keys

    def get_customfields(self):
        endpoint = f"{self.base_url}/rest/api/3/field"

        customfields = self.send_request(endpoint)

        if customfields is not None:
            return {item["id"]: item["name"] for item in customfields}

        return customfields

    def get_issue(self, issue_id):
        # Jira REST API 엔드포인트
        endpoint = f"{self.base_url}/rest/api/3/issue/{issue_id}"

        issue = self.send_request(endpoint)
        # print("issue:", issue)

        if issue is not None:
            projectKey = issue["fields"]["project"]["key"]
            key = issue["key"]
            summary = issue["fields"]["summary"]
            status = issue["fields"]["status"]["name"]
            print(f"issue_type: {issue['fields']['issuetype']}")
            issue_type = issue["fields"]["issuetype"]["name"]
            updated = issue["fields"]["updated"]
            comments = issue["fields"]["comment"]["comments"]
            if issue["fields"]["assignee"] is not None:
                assignee = issue["fields"]["assignee"]["displayName"]
            else:
                assignee = "No assignee"
            customfields_text = get_customfield_values(issue, self.customfields)

            description = issue["fields"]["description"]
            description_text = " ".join(extract_texts(description))

            comment_text = ""
            for comment in comments:
                comment_displayName = comment["author"]["displayName"]
                # comment_content = get_comments_text(comment["body"])
                comment_content = " ".join(get_comments_text(comment["body"]))
                comment_updated = format_date_simple(comment["updated"])
                comment_text += (
                    f"[댓글]\n"
                    f"{comment_displayName}, {comment_updated}\n"
                    f"{comment_content}\n\n"
                )

            return {
                "project_key": projectKey,
                "key": key,
                "summary": summary,
                "status": status,
                "issue_type": issue_type,
                "assignee": assignee,
                "description_text": description_text,
                "customfields_text": customfields_text,
                "comment_text": comment_text,
                "updated": updated,
            }
        else:
            return None

    def create_issue(self, project_key, issue_type, summary, content):
        issue_type = "10351"  # 작업
        issue_type = "10113"  # 스토리

        project = self.get_project(project_key)
        # print(project)
        project_id = project["project_id"]

        endpoint = f"{self.base_url}/rest/api/3/issue"

        data = {
            "fields": {
                # "assignee": {"id": "5b109f2e9729b51b54dc274d"},
                # "components": [{"id": "10000"}],
                "description": {
                    "content": [
                        {
                            "content": [
                                {
                                    "text": content,
                                    "type": "text",
                                }
                            ],
                            "type": "paragraph",
                        }
                    ],
                    "type": "doc",
                    "version": 1,
                },
                "issuetype": {"id": issue_type},
                "project": {"id": project_id},
                "summary": summary,
            },
            "update": {},
        }
        print(f"[create_issue] data: {data}")
        response = self.send_request(endpoint, method="POST", data=data)
        print(f"[create_issue] response: {response}")

        return response


if __name__ == "__main__":
    jira = EnomixJira()
    # print(jira.get_project("AVGRS"))
    # print(jira.get_customfields())
    jql = "project = \"AVGRS\" AND updated >= '2023-01-01' "
    print(jira.get_issue_list(jql))
    # result = jira.get_issue("AVGRS-793")
    # print(result)
    # jira.create_issue("AVGRS", "10351", "제목", "내용")
