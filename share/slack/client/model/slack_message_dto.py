from typing import Optional

from pydantic import BaseModel

from share.slack.util.util import Util


class SlackMessageDto(BaseModel):
    ts: str
    user: Optional[str] = ""
    text: str
    thread_ts: Optional[str] = ""
    reply_users: Optional[list] = ()

    def __init__(self, user_dict=None, **data):
        super().__init__(**data)
        if user_dict is not None:
            self.reply_users = [
                user_dict.get(user_id, user_id) for user_id in self.reply_users
            ]
            self.user = user_dict.get(self.user, self.user)
            self.text = Util.replace_ids_with_names(self.text, user_dict)
