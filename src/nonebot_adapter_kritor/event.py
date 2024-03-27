from copy import deepcopy
from typing_extensions import override
from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Optional, Union
from datetime import datetime
from pydantic import Field
from nonebot.utils import escape_tag
from nonebot.compat import PYDANTIC_V2, model_dump, type_validate_python

from nonebot.adapters import Event as BaseEvent

from .compat import model_validator
from .model import ContactType, Sender, Group, Friend, Stranger, Guild, StrangerFromGroup, Nearby
from .message import Message, Reply

class Event(BaseEvent):

    @override
    def get_type(self) -> str:
        return ""

    @override
    def get_event_name(self) -> str:
        return ""

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(model_dump(self)))

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def is_tome(self) -> bool:
        return False


class MessageEvent(Event):
    time: datetime
    message_id: str
    message_seq: int
    contact: ContactType
    sender: Sender
    to_me: bool = False
    reply: Optional[Reply] = None

    message: Message
    original_message: Message

    if TYPE_CHECKING:
        _replied_message: "MessageEvent"

    @property
    def replied_message(self) -> Optional["MessageEvent"]:
        return getattr(self, "_replied_message", None)

    @override
    def get_type(self) -> str:
        return "message"

    @override
    def get_event_name(self) -> str:
        # 返回事件的名称，用于日志打印
        return "message"

    @override
    def is_tome(self) -> bool:
        return self.to_me

    @override
    def get_message(self) -> Message:
        return self.message

    @model_validator(mode="before")
    def generate_message(cls, values: dict[str, Any]):
        values["message"] = Message.from_elements(values["elements"])
        values["original_message"] = deepcopy(values["message"])
        return values

    @override
    def get_user_id(self) -> str:
        return f"{self.sender.uin or self.sender.uid}"

    @override
    def get_session_id(self) -> str:
        ids = [self.contact.id, f"{self.sender.uin or self.sender.uid}"]
        if self.contact.sub_id:
            ids.insert(1, self.contact.sub_id)
        return "_".join(ids)


class FriendMessage(MessageEvent):
    contact: Friend

    @override
    def get_event_name(self) -> str:
        return "message.friend"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from {self.sender.nick or self.sender.uin or self.sender.uid}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

class GroupMessage(MessageEvent):
    contact: Group

    @override
    def get_event_name(self) -> str:
        return "message.group"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from {self.sender.nick or self.sender.uin or self.sender.uid} "
            f"in group {self.contact.id}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

class GuildMessage(MessageEvent):
    contact: Guild

    @override
    def get_event_name(self) -> str:
        return "message.guild"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from {self.sender.nick or self.sender.uin or self.sender.uid} "
            f"in guild {self.contact.id}/{self.contact.sub_id or ''}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

class StrangerMessage(MessageEvent):
    contact: Stranger

    @override
    def get_event_name(self) -> str:
        return "message.stranger"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from stranger {self.sender.nick or self.sender.uin or self.sender.uid}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

class TempMessage(MessageEvent):
    contact: StrangerFromGroup

    @override
    def get_event_name(self) -> str:
        return "message.temp"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from stranger in group {self.contact.id}, "
            f"{self.sender.nick or self.sender.uin or self.sender.uid}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

class NearbyMessage(MessageEvent):
    contact: Nearby

    @override
    def get_event_name(self) -> str:
        return "message.nearby"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from nearby {self.sender.nick or self.sender.uin or self.sender.uid}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

MessageEventType = Union[
    Union[GroupMessage, FriendMessage, GuildMessage, StrangerMessage, TempMessage, NearbyMessage],
    MessageEvent,
]
