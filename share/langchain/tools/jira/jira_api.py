import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

# Jira Cloud 계정 정보
email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")
base_url = os.getenv("JIRA_BASE_URL")

# HTTP 요청 헤더 설정
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

auth = HTTPBasicAuth(email, api_token)


def send_request(endpoint, method="GET", data=None):
    if method == "GET":
        response = requests.get(endpoint, headers=headers, auth=auth)
    elif method == "POST":
        response = requests.post(endpoint, headers=headers, auth=auth, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")

    if response.status_code != 200:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    return response.json()
