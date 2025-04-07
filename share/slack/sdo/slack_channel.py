from pydantic import BaseModel


class SlackChannelRdo(BaseModel):
    id: str
    name: str
    is_member: bool


class SlackChannelRdoListRdo(object):
    channels: list[SlackChannelRdo]
    next_cursor: str

    def __init__(self, channels, next_cursor):
        self.channels = channels
        self.next_cursor = next_cursor

    def to_dict(self):
        dic = {}
        for channel in self.channels:
            dic[channel.id] = channel.name
        return dic

    def __str__(self):
        return str(self.channels)
