import pprint

from share.slack.service.slack_channel_service import SlackChannelService
from share.slack.service.slack_message_service import SlackMessageService

pp = pprint.PrettyPrinter(width=60, compact=True)


def print_array(arr: list):
    for v in arr:
        pp.pprint(dict(v))


if __name__ == "__main__":
    slack_message_service = SlackMessageService()
    slack_channel_service = SlackChannelService()
    sample_channel_id = "C06G2M66F7B"
    # slack channel에 봇을 join 시킵니다.
    slack_channel_service.join_channel("C06G2M66F7B")

    # slack message 3개와 해당 쓰레드를 가져옵니다.
    # 해당 채널에 봇이 추가되어 있지 않으면 메시지를 가져올 수 없습니다!
    slack_message_result = slack_message_service.get_messages(
        sample_channel_id, limit=3
    )

    print_array(slack_message_result.messages)

    # next 조회
    slack_next_message_result = slack_message_service.get_messages(
        sample_channel_id, limit=3, next_cursor=slack_message_result.next_cursor
    )

    print_array(slack_next_message_result.messages)
