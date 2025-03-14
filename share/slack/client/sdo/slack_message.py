from typing import Optional

from pydantic import BaseModel


class SlackThread(BaseModel):
    ts: str
    user: str
    text: str


class SlackMessage(BaseModel):
    user: str
    text: str
    ts: str
    channel_id: str
    thread_ts: str
    reply_users: Optional[list[str]]
    thread_messages: Optional[list[SlackThread]]

    def __init__(self, **data):
        super().__init__(**data)

        if self.thread_messages is None:
            self.thread_messages = []


class SlackMessages(object):
    messages: list[SlackMessage]
    is_continue: bool
    next_cursor: str

    def __init__(self, messages, is_continue, next_cursor):
        self.messages = messages
        self.is_continue = is_continue
        self.next_cursor = next_cursor
