from share.slack.sdo.slack_channel import (
    SlackChannelRdoListRdo,
    SlackChannelRdo,
)
from share.slack.client.slack_channel_client import SlackChannelClient
from share.slack.exception.slack_exception import SlackChannelError
from share.slack.util.logger import setup_logger
from share.slack.util.retry import RetryUtil

logger = setup_logger(__name__)


class SlackChannelService:
    """Slack 채널 서비스"""

    def __init__(self) -> None:
        self.client: SlackChannelClient = SlackChannelClient()
        logger.info("SlackChannelService initialized")

    @RetryUtil.retry(max_retries=3, delay=1.0, backoff=2.0)
    def join_channel(self, channel_id: str) -> bool:
        """채널 참여"""
        try:
            logger.info(f"Attempting to join channel {channel_id}")
            result = self.client.join_channel(channel_id)
            if not result.get("ok"):
                error_message = result.get("error", "Unknown error")
                logger.error(f"Failed to join channel: {error_message}")
                raise SlackChannelError(error_message)
            logger.info(f"Successfully joined channel {channel_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to join channel: {str(e)}")
            raise SlackChannelError(f"Failed to join channel: {str(e)}")

    @RetryUtil.retry(max_retries=3, delay=1.0, backoff=2.0)
    def get_channels(self, next_cursor=""):
        """채널 조회"""
        try:
            logger.info(f"next_cursor :  {next_cursor}")
            result = self.client.get_channels(next_cursor=next_cursor)

            if not result.get("ok"):
                error_message = result.get("error", "Unknown error")
                logger.error(f"Failed to get channel: {error_message}")
                raise SlackChannelError(error_message)

            logger.info(f"Successfully retrieved all {len(result.get('channels'))}")
            return SlackChannelRdoListRdo(
                [SlackChannelRdo(**channel) for channel in result.get("channels")],
                result.get("response_metadata", {next_cursor: ""}).get(
                    "next_cursor", ""
                ),
            )
        except Exception as e:
            logger.error(f"Failed to join channel: {str(e)}")
            raise SlackChannelError(f"Failed to get channels: {str(e)}")

    def get_all_channels(self) -> SlackChannelRdoListRdo:
        """모든 채널 조회"""
        channels = []
        next_cursor = ""
        while True:
            channels_res = self.get_channels(next_cursor)
            channels.extend(channels_res.channels)
            next_cursor = channels_res.next_cursor
            if channels_res.next_cursor == "":
                break
        return SlackChannelRdoListRdo(channels, "")

    def get_all_joined_channels(self):
        """해당 봇에 권한이 있는 모든 채널 조회"""
        all_channels = self.get_all_channels().channels
        logger.info(f"all channels cnt : {len(all_channels)}")
        joined_channels = [channel for channel in all_channels if channel.is_member]
        logger.info(f"joined channels cnt : {len(joined_channels)}")
        return SlackChannelRdoListRdo(joined_channels, "")


if __name__ == "__main__":
    service = SlackChannelService()
    for k, v in service.get_all_joined_channels().to_dict().items():
        print(k, v)
