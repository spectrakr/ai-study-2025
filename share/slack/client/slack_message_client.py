import json

import requests

from share.slack.config import get_slack_bot_token


class SlackMessageClient(object):
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
            "Authorization": f"Bearer {get_slack_bot_token()}",
            "Content-type": "application/json;charset=UTF-8",
        }

    def get_messages(self, channel_id, next_cursor="", limit=100):
        url = f"https://slack.com/api/conversations.history?channel={channel_id}&limit={limit}&cursor={next_cursor}"
        return self.session.get(url).json()

    def get_message_by_ts(self, channel_id, ts):
        url = f"https://slack.com/api/conversations.replies?channel={channel_id}&ts={ts}&limit=1&inclusive=true"
        return self.session.get(url).json()

    def get_thread(self, channel_id, ts):
        url = (
            f"https://slack.com/api/conversations.replies?channel={channel_id}&ts={ts}"
        )
        return self.session.post(url).json()

    def post_message(self, channel_id, message):
        url = f"https://slack.com/api/chat.postMessage"
        return self.session.post(
            url, data=json.dumps({"text": message, "channel": channel_id})
        ).json()


if __name__ == "__main__":
    client = SlackMessageClient()
    print(client.post_message("C08DXE0FJJE", "test"))
