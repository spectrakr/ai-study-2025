import os

from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


def get_slack_bot_token():
    return SLACK_BOT_TOKEN
