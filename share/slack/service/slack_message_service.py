from typing import List, Dict, Any
from share.slack.client.slack_message_client import SlackMessageClient
from share.slack.client.model.slack_message_dto import SlackMessageDto
from share.slack.client.sdo.slack_message import (
    SlackMessage,
    SlackThread,
    SlackMessages,
)
from share.slack.util.util import Util
from share.slack.exception.slack_exception import SlackMessageError, SlackAPIError
from share.slack.util.logger import setup_logger
from share.slack.util.retry import RetryUtil

logger = setup_logger(__name__)


class SlackMessageService:
    """Slack 메시지 서비스"""

    def __init__(self) -> None:
        self.client: SlackMessageClient = SlackMessageClient()
        self.user_dict: Dict[str, str] = Util.get_members_dict()
        logger.info("SlackMessageService initialized")

    @RetryUtil.retry(max_retries=3, delay=1.0, backoff=2.0)
    def get_messages(
        self, channel_id: str, limit: int = 10, next_cursor: str = ""
    ) -> SlackMessages:
        """메시지 목록 조회"""
        try:
            logger.info(
                f"Getting messages from channel {channel_id} with limit {limit}"
            )
            message_result: Dict[str, Any] = self.client.get_messages(
                channel_id, limit=limit, next_cursor=next_cursor
            )

            if not message_result.get("ok"):
                error_message: str = message_result.get("error", "Unknown error")
                logger.error(f"Failed to get messages: {error_message}")
                raise SlackAPIError(error_message)

            messages: List[SlackMessage] = []
            for m in message_result["messages"]:
                message_dto: SlackMessageDto = SlackMessageDto(
                    user_dict=self.user_dict, **m
                )
                messages.append(
                    SlackMessage(
                        **dict(message_dto),
                        channel_id=channel_id,
                        thread_messages=self._get_threads(channel_id, message_dto),
                    )
                )

            logger.info(f"Successfully retrieved {len(messages)} messages")
            return SlackMessages(
                messages=messages,
                is_continue=message_result.get("has_more", False),
                next_cursor=message_result.get("response_metadata", {}).get(
                    "next_cursor", ""
                ),
            )
        except Exception as e:
            if isinstance(e, SlackAPIError):
                raise
            logger.error(f"Failed to get messages: {str(e)}")
            raise SlackMessageError(f"Failed to get messages: {str(e)}")

    @RetryUtil.retry(max_retries=3, delay=1.0, backoff=2.0)
    def all_channel_messages(self, channel_id: str) -> List[SlackMessage]:
        """채널의 모든 메시지 조회"""
        try:
            logger.info(f"Getting all messages from channel {channel_id}")
            next_cursor: str = ""
            is_continue: bool = True
            messages: List[SlackMessage] = []

            while is_continue:
                message_result: SlackMessages = self.get_messages(
                    channel_id, next_cursor=next_cursor
                )
                is_continue = message_result.is_continue
                next_cursor = message_result.next_cursor
                messages.extend(message_result.messages)
                logger.debug(f"Retrieved {len(messages)} messages so far")

            logger.info(f"Successfully retrieved all {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"Failed to get all channel messages: {str(e)}")
            raise SlackMessageError(f"Failed to get all channel messages: {str(e)}")

    @RetryUtil.retry(max_retries=3, delay=1.0, backoff=2.0)
    def _get_threads(
        self, channel_id: str, message: SlackMessageDto
    ) -> List[SlackThread]:
        """스레드 메시지 조회"""
        try:
            logger.debug(
                f"Getting threads for message {message.ts} in channel {channel_id}"
            )
            thread_result: Dict[str, Any] = self.client.get_thread(
                channel_id, message.thread_ts
            )

            if not thread_result.get("ok"):
                return []

            threads: List[SlackThread] = [
                SlackThread(**dict(thread))
                for thread in map(
                    lambda thread: SlackMessageDto(user_dict=self.user_dict, **thread),
                    thread_result["messages"],
                )
            ]

            logger.debug(f"Found {len(threads)} threads for message {message.ts}")
            return threads

        except Exception as e:
            if isinstance(e, SlackAPIError):
                raise
            logger.error(f"Failed to get thread messages: {str(e)}")
            raise SlackMessageError(f"Failed to get thread messages: {str(e)}")

    @RetryUtil.retry(max_retries=3, delay=1.0, backoff=2.0)
    def send_message(self, channel_id: str, text: str):
        """메시지 보내기"""
        try:
            logger.debug(f" send message channel_id : {channel_id},  message: {text}")

            self.client.post_message(channel_id, text)

            logger.debug(
                f" Successfully send message channel_id : {channel_id},  message: {text}"
            )
        except Exception as e:
            if isinstance(e, SlackAPIError):
                raise
            logger.error(f"Failed to send message: {str(e)}")
            raise SlackMessageError(f"Failed to send message: {str(e)}")


# if __name__ == "__main__":
#     service = SlackMessageService()
#     try:
#         for message in service.get_messages("C06G2M66F7B").messages:
#             print(f"{message.user}  {message.ts}: {message.text} \n ")
#             print(
#                 "\n".join(
#                     ["thread"]
#                     + list(
#                         map(
#                             lambda thread: f"{thread.user} {thread.ts}: {thread.text}",
#                             message.thread_messages,
#                         )
#                     )
#                     + ["thread end"]
#                 )
#             )
#     except SlackMessageError as e:
#         logger.error(f"Error getting messages: {e}")
#         print(f"Error getting messages: {e}")
#     except SlackAPIError as e:
#         logger.error(f"Slack API error: {e}")
#         print(f"Slack API error: {e}")
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         print(f"Unexpected error: {e}")

if __name__ == "__main__":
    service = SlackMessageService()
    service.send_message("C08DXE0FJJE", "test")
