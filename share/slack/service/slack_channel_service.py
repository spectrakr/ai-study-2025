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
