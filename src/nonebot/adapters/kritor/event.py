from copy import deepcopy
from datetime import datetime
from typing_extensions import override
from typing import TYPE_CHECKING, Any, Union, Literal, Optional

from pydantic import Field
from nonebot.utils import escape_tag
from nonebot.compat import model_dump

from nonebot.adapters import Event as BaseEvent

from .compat import model_validator
from .message import Reply, Message
from .model import Group, Guild, Friend, Nearby, Sender, Stranger, ContactType, StrangerFromGroup
from .protos.kritor.event import (
    GroupMemberBanNoticeGroupMemberBanType,
    GroupMemberDecreasedNoticeGroupMemberDecreasedType,
    GroupMemberIncreasedNoticeGroupMemberIncreasedType,
)

if TYPE_CHECKING:
    from .bot import Bot


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
        """返回可能的回复元素代表的原消息事件。"""
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
        text = f"Message from {self.sender.nick or self.sender.uin or self.sender.uid}: " f"{self.get_message()}"
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
            f"Message from stranger {self.sender.nick or self.sender.uin or self.sender.uid}: " f"{self.get_message()}"
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
        text = f"Message from nearby {self.sender.nick or self.sender.uin or self.sender.uid}: " f"{self.get_message()}"
        return escape_tag(text)


MessageEventType = Union[
    Union[GroupMessage, FriendMessage, GuildMessage, StrangerMessage, TempMessage, NearbyMessage],
    MessageEvent,
]


class RequestEvent(Event):
    __type__: str
    time: datetime

    @override
    def get_type(self) -> str:
        return "request"

    @override
    def get_event_name(self) -> str:
        return f"request.{self.__type__}"

    @override
    def is_tome(self) -> bool:
        return True


class FriendApplyRequest(RequestEvent):
    __type__: Literal["friend_apply"] = "friend_apply"

    applier_uid: str
    applier_uin: int
    flag: str
    message: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend apply from {self.applier_uid or self.applier_uin}: {self.message}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.applier_uin or self.applier_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.applier_uin or self.applier_uid}"


class GroupApplyRequest(RequestEvent):
    __type__: Literal["group_apply"] = "group_apply"

    group_id: int
    applier_uid: str
    applier_uin: int
    inviter_uid: str
    inviter_uin: int
    reason: str
    flag: str

    @override
    def get_event_description(self) -> str:
        text = f"Group apply from {self.applier_uid or self.applier_uin} " f"in group {self.group_id}: {self.reason}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.applier_uin or self.applier_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.applier_uin or self.applier_uid}"


class InvitedJoinGroupRequest(RequestEvent):
    __type__: Literal["invited_group"] = "invited_group"

    group_id: int
    inviter_uid: str
    inviter_uin: int
    flag: str

    @override
    def get_event_description(self) -> str:
        text = f"Invited to group {self.group_id} by {self.inviter_uid or self.inviter_uin}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.inviter_uin or self.inviter_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.inviter_uin or self.inviter_uid}"


RequestEventType = Union[
    Union[FriendApplyRequest, GroupApplyRequest, InvitedJoinGroupRequest],
    RequestEvent,
]


class NoticeEvent(Event):
    __type__: str
    time: datetime
    to_me: bool = False

    @override
    def get_type(self) -> str:
        return "notice"

    @override
    def get_event_name(self) -> str:
        return f"notice.{self.__type__}"

    @override
    def is_tome(self) -> bool:
        return self.to_me

    def check_tome(self, bot: "Bot") -> None:
        if not self.is_tome():
            self.to_me = self.get_user_id() == bot.self_id


class PrivatePokeNotice(NoticeEvent):
    __type__: Literal["private_poke"] = "private_poke"

    operator_uid: str
    operator_uin: int
    action: str
    suffix: str
    action_image: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.operator_uid or self.operator_uin} send nudge"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def is_tome(self) -> bool:
        return True


class PrivateRecallNotice(NoticeEvent):
    __type__: Literal["private_recall"] = "private_recall"

    operator_uid: str
    operator_uin: int
    message_id: str
    tip_text: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.operator_uid or self.operator_uin} recall message {self.message_id}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def is_tome(self) -> bool:
        return True


class GroupUniqueTitleChangedNotice(NoticeEvent):
    __type__: Literal["group_member_unique_title_changed"] = "group_member_unique_title_changed"

    target: int
    title: str
    group_id: int

    @override
    def get_event_description(self) -> str:
        text = f"{self.target}'s unique title in Group {self.group_id} changed to {self.title}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target}"


class GroupEssenceMessageNotice(NoticeEvent):
    __type__: Literal["group_essence_changed"] = "group_essence_changed"

    group_id: int
    operator_uid: str
    operator_uin: int
    target_uid: str
    target_uin: int
    message_id: str
    sub_type: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} essence message {self.message_id} changed by {self.operator_uid or self.operator_uin}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.operator_uin or self.operator_uid}"

    @override
    def check_tome(self, bot: "Bot") -> None:
        self.to_me = f"{self.target_uin or self.target_uid}" == bot.self_id


class GroupPokeNotice(NoticeEvent):
    __type__: Literal["group_poke"] = "group_poke"

    group_id: int
    operator_uid: str
    operator_uin: int
    target_uid: str
    target_uin: int
    action: str
    suffix: str
    action_image: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uid or self.operator_uin} send nudge"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.operator_uin or self.operator_uid}"

    @override
    def check_tome(self, bot: "Bot") -> None:
        self.to_me = f"{self.target_uin or self.target_uid}" == bot.self_id


class GroupCardChangedNotice(NoticeEvent):
    __type__: Literal["group_card_changed"] = "group_card_changed"

    group_id: int
    operator_uid: str
    operator_uin: int
    target_uid: str
    target_uin: int
    new_card: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uid or self.operator_uin} change {self.target_uid or self.target_uin}'s card to {self.new_card}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.operator_uin or self.operator_uid}"

    @override
    def check_tome(self, bot: "Bot") -> None:
        self.to_me = f"{self.target_uin or self.target_uid}" == bot.self_id


class GroupMemberIncreasedNotice(NoticeEvent):
    __type__: Literal["group_member_increase"] = "group_member_increase"

    group_id: int
    operator_uid: str
    operator_uin: int
    target_uid: str
    target_uin: int

    flag: GroupMemberIncreasedNoticeGroupMemberIncreasedType = Field(..., alias="type")

    @override
    def get_event_description(self) -> str:
        text = f"New member {self.target_uid or self.target_uin} joined Group {self.group_id} by {self.operator_uid or self.operator_uin}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target_uin or self.target_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target_uin or self.target_uid}"


class GroupMemberDecreasedNotice(NoticeEvent):
    __type__: Literal["group_member_decrease"] = "group_member_decrease"

    group_id: int
    operator_uid: str
    operator_uin: int
    target_uid: str
    target_uin: int

    flag: GroupMemberDecreasedNoticeGroupMemberDecreasedType = Field(..., alias="type")

    @override
    def get_event_description(self) -> str:
        text = f"Member {self.target_uid or self.target_uin} left Group {self.group_id} by {self.operator_uid or self.operator_uin}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target_uin or self.target_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target_uin or self.target_uid}"


class GroupAdminChangedNotice(NoticeEvent):
    __type__: Literal["group_admin_change"] = "group_admin_change"

    group_id: int
    target_uid: str
    target_uin: int
    is_admin: bool

    @override
    def get_event_description(self) -> str:
        text = (
            f"Group {self.group_id} {self.target_uid or self.target_uin} become admin"
            if self.is_admin
            else f"Group {self.group_id} {self.target_uid or self.target_uin} lose admin"
        )
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target_uin or self.target_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target_uin or self.target_uid}"


class GroupMemberBanNotice(NoticeEvent):
    __type__: Literal["group_member_ban"] = "group_member_ban"

    group_id: int
    operator_uid: str
    operator_uin: int
    target_uid: str
    target_uin: int
    duration: int

    flag: GroupMemberBanNoticeGroupMemberBanType = Field(..., alias="type")

    @override
    def get_event_description(self) -> str:
        text = (
            (
                f"Group {self.group_id} {self.target_uid or self.target_uin} banned by {self.operator_uid or self.operator_uin}"
            )
            if self.duration
            else (
                f"Group {self.group_id} {self.target_uid or self.target_uin} unbanned by {self.operator_uid or self.operator_uin}"
            )
        )
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target_uin or self.target_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target_uin or self.target_uid}"


class GroupRecallNotice(NoticeEvent):
    __type__: Literal["group_recall"] = "group_recall"

    group_id: int
    message_id: str
    tip_text: str
    operator_uid: str
    operator_uin: int
    target_uid: str
    target_uin: int
    message_seq: int

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uid or self.operator_uin} recall message {self.message_id}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.operator_uin or self.operator_uid}"

    @override
    def check_tome(self, bot: "Bot") -> None:
        self.to_me = f"{self.target_uin or self.target_uid}" == bot.self_id


class GroupSignInNotice(NoticeEvent):
    __type__: Literal["group_sign_in"] = "group_sign_in"

    group_id: int
    target_uid: str
    target_uin: int
    action: str
    suffix: str
    rank_image: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.target_uid or self.target_uin} sign in"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target_uin or self.target_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target_uin or self.target_uid}"

    @override
    def is_tome(self) -> bool:
        return False


class GroupWholeBanNotice(NoticeEvent):
    __type__: Literal["group_whole_ban"] = "group_whole_ban"

    group_id: int
    operator_uid: str
    operator_uin: int
    is_ban: bool

    @override
    def get_event_description(self) -> str:
        text = (
            f"Group {self.group_id} whole banned by {self.operator_uid or self.operator_uin} "
            if self.is_ban
            else f"Group {self.group_id} whole unbanned by {self.operator_uid or self.operator_uin}"
        )
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.operator_uin or self.operator_uid}"

    @override
    def is_tome(self) -> bool:
        return True


class GroupReactMessageWithEmojiNotice(NoticeEvent):
    __type__: Literal["group_react_message_with_emoji"] = "group_react_message_with_emoji"

    group_id: int
    message_id: str
    face_id: int
    is_set: bool

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message {self.message_id} in Group {self.group_id} reacted with emoji {self.face_id}"
            if self.is_set
            else f"Message {self.message_id} in Group {self.group_id} unreacted with emoji {self.face_id}"
        )
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.message_id}"

    @override
    def is_tome(self) -> bool:
        return False


class PrivateFileUploadedNotice(NoticeEvent):
    __type__: Literal["private_file_uploaded"] = "private_file_uploaded"

    operator_uid: str
    operator_uin: int
    file_id: str
    file_sub_id: int
    file_name: str
    file_size: int
    expire_time: datetime
    file_url: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.operator_uid or self.operator_uin} uploaded file {self.file_name}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def is_tome(self) -> bool:
        return True


class GroupFileUploadedNotice(NoticeEvent):
    __type__: Literal["group_file_uploaded"] = "group_file_uploaded"

    group_id: int
    operator_uid: str
    operator_uin: int
    file_id: str
    file_sub_id: int
    file_name: str
    file_size: int
    expire_time: datetime
    file_url: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uid or self.operator_uin} uploaded file {self.file_name}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.operator_uin or self.operator_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.operator_uin or self.operator_uid}"

    @override
    def is_tome(self) -> bool:
        return False


NoticeEventType = Union[
    Union[
        PrivatePokeNotice,
        PrivateRecallNotice,
        GroupUniqueTitleChangedNotice,
        GroupEssenceMessageNotice,
        GroupPokeNotice,
        GroupCardChangedNotice,
        GroupMemberIncreasedNotice,
        GroupMemberDecreasedNotice,
        GroupAdminChangedNotice,
        GroupMemberBanNotice,
        GroupRecallNotice,
        GroupSignInNotice,
        GroupWholeBanNotice,
        PrivateFileUploadedNotice,
        GroupFileUploadedNotice,
        GroupReactMessageWithEmojiNotice,
    ],
    NoticeEvent,
]
