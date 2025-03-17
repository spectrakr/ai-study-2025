import requests

from share.slack.config import get_slack_bot_token


class SlackChannelClient(object):
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {"Authorization": f"Bearer {get_slack_bot_token()}"}

    def join_channel(self, channel_id):
        url = "https://slack.com/api/conversations.join"
        return self.session.post(url, data={"channel": channel_id}).json()

    def get_channels(self, next_cursor=""):
        url = f"https://slack.com/api/conversations.list?cursor={next_cursor}"
        return self.session.get(url).json()


if __name__ == "__main__":
    client = SlackChannelClient()
    print(client.get_channels())
