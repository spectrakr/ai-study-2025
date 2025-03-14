import requests

from share.slack.config import get_slack_bot_token


class SlackChannelClient(object):
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {"Authorization": f"Bearer {get_slack_bot_token()}"}

    def join_channel(self, channel_id):
        url = "https://slack.com/api/conversations.join"
        return self.session.post(url, data={"channel": channel_id}).json()
