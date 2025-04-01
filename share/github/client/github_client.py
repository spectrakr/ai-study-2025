import os
import pprint

import requests
from dotenv import load_dotenv

from share.slack.util.logger import setup_logger

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

logger = setup_logger(__name__)


class GitHubClient:
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    @classmethod
    def get_pr_diff(cls, pr_url):
        logger.info(f"get pr-url :{pr_url}")
        response = requests.get(pr_url, headers=cls.headers)
        if response.status_code == 200:
            pr_data = response.json()
            files_url = pr_data["url"] + "/files"  # PR의 변경된 파일 가져오기
            files_response = requests.get(files_url, headers=cls.headers)
            logger.info(files_response)
            if files_response.status_code == 200:
                return files_response.json()
        return None

    @classmethod
    def post_review_comment(cls, url, file_name, review_text):
        post_url = f"{url}/comments"
        data = {
            "body": f"{file_name} \n {review_text}",
        }
        logger.info(f"issue url : {post_url}")
        logger.info(data)
        response = requests.post(post_url, json=data, headers=cls.headers)
        return response.json()

    @staticmethod
    def replace_pr_api_url(u: str):
        return u.replace("github.com", "api.github.com/repos").replace("pull", "pulls")

    @staticmethod
    def replace_issue_api_url(u: str):
        return u.replace("github.com", "api.github.com/repos").replace("pull", "issues")


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(width=60, compact=True)
    u = "https://github.com/spectrakr/gmo-victory-talk-ui-customer/pull/8"

    issue_url = GitHubClient.replace_issue_api_url(u)
    print(GitHubClient.post_review_comment(issue_url, "test", "test"))
