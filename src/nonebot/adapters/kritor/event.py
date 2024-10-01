from copy import deepcopy
from datetime import datetime
from typing_extensions import override
from typing import TYPE_CHECKING, Any, Union, Literal, Optional

from pydantic import Field
from nonebot.utils import escape_tag
from nonebot.compat import PYDANTIC_V2, ConfigDict, model_dump

from nonebot.adapters import Event as BaseEvent

from .message import Reply, Message
from .protos.kritor.common import Scene
from .compat import field_validator, model_validator
from .model import Contact, SceneType, GroupSender, GuildSender, PrivateSender
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

    if PYDANTIC_V2:
        model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)  # type: ignore
    else:

        class Config:
            extra = "allow"
            arbitrary_types_allowed = True


SenderType = Union[PrivateSender, GroupSender, GuildSender]


class MessageEvent(Event):
    time: datetime
    message_id: str
    message_seq: int
    scene: SceneType
    sender: SenderType
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

    @field_validator("scene", mode="before")
    def check_scene(cls, v):
        if v is None:
            return SceneType.GROUP
        if isinstance(v, SceneType):
            return v
        if isinstance(v, int):
            return SceneType(v)
        if isinstance(v, Scene):
            return SceneType(v.value)
        if isinstance(v, str) and v.upper() in SceneType.__members__:
            return SceneType.__members__[v.upper()]
        raise ValueError(f"invalid scene: {v}")

    @model_validator(mode="before")
    def generate_message_and_sender(cls, values: dict[str, Any]):
        values["message"] = Message.from_elements(values["elements"])
        values["original_message"] = deepcopy(values["message"])
        if "private" in values:
            values["sender"] = values.pop("private")
        elif "group" in values:
            values["sender"] = values.pop("group")
        elif "guild" in values:
            values["sender"] = values.pop("guild")
        if "scene" not in values:
            values["scene"] = SceneType.UNSPECIFIED
        return values

    @override
    def get_user_id(self) -> str:
        if isinstance(self.sender, (PrivateSender, GroupSender)):
            return f"{self.sender.uin or self.sender.uid}"
        return self.sender.tiny_id

    @override
    def get_session_id(self) -> str:
        if isinstance(self.sender, GroupSender):
            return f"{self.sender.group_id}_{self.sender.uin or self.sender.uid}"
        if isinstance(self.sender, GuildSender):
            return f"{self.sender.guild_id}_{self.sender.channel_id}_{self.sender.tiny_id}"
        return f"{self.sender.uin or self.sender.uid}"

    @property
    def contact(self) -> "Contact":
        if isinstance(self.sender, GuildSender):
            return Contact(type=self.scene, id=self.sender.channel_id, sub_id=self.sender.guild_id)
        if isinstance(self.sender, GroupSender):
            return Contact(type=self.scene, id=self.sender.group_id, sub_id=None)
        return Contact(type=self.scene, id=self.get_user_id(), sub_id=None)


class FriendMessage(MessageEvent):
    scene: Literal[SceneType.FRIEND]
    sender: PrivateSender

    to_me: bool = True

    @override
    def get_event_name(self) -> str:
        return "message.friend"

    @override
    def get_event_description(self) -> str:
        text = f"Message from {self.sender.nick or self.sender.uin or self.sender.uid}: " f"{self.get_message()}"
        return escape_tag(text)


class GroupMessage(MessageEvent):
    scene: Literal[SceneType.GROUP]
    sender: GroupSender

    @override
    def get_event_name(self) -> str:
        return "message.group"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from {self.sender.nick or self.sender.uin or self.sender.uid} "
            f"in group {self.sender.group_id}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

    @property
    def contact_private(self) -> "Contact":
        return Contact(type=SceneType.FRIEND, id=self.get_user_id())

    @property
    def contact_temp(self) -> "Contact":
        return Contact(type=SceneType.STRANGER_FROM_GROUP, id=self.get_user_id(), sub_id=self.sender.group_id)


class GuildMessage(MessageEvent):
    scene: Literal[SceneType.GUILD]
    sender: GuildSender

    @override
    def get_event_name(self) -> str:
        return "message.guild"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from {self.sender.nick or self.sender.tiny_id} "
            f"in guild {self.sender.guild_id}/{self.sender.channel_id or ''}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)


class StrangerMessage(MessageEvent):
    scene: Literal[SceneType.STRANGER]
    sender: PrivateSender

    to_me: bool = True

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
    scene: Literal[SceneType.STRANGER_FROM_GROUP]
    sender: GroupSender

    to_me: bool = True

    @override
    def get_event_name(self) -> str:
        return "message.temp"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from stranger in group {self.sender.group_id}, "
            f"{self.sender.nick or self.sender.uin or self.sender.uid}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

    @property
    def contact(self) -> "Contact":
        return Contact(type=SceneType.STRANGER_FROM_GROUP, id=self.get_user_id(), sub_id=self.sender.group_id)

    @property
    def contact_private(self) -> "Contact":
        return Contact(type=SceneType.FRIEND, id=self.get_user_id())

    @property
    def contact_group(self) -> "Contact":
        return Contact(type=SceneType.GROUP, id=self.sender.group_id)


class NearbyMessage(MessageEvent):
    scene: Literal[SceneType.NEARBY]
    sender: PrivateSender

    to_me: bool = True

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

    applier_uid: Optional[str] = None
    applier_uin: int
    message: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend apply from {self.applier_uin or self.applier_uid}: {self.message}"
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
    applier_uid: Optional[str] = None
    applier_uin: int
    inviter_uid: Optional[str] = None
    inviter_uin: Optional[int] = None
    reason: str

    @override
    def get_event_description(self) -> str:
        text = f"Group apply from {self.applier_uin or self.applier_uid} " f"in group {self.group_id}: {self.reason}"
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
    inviter_uid: Optional[str] = None
    inviter_uin: int

    @override
    def get_event_description(self) -> str:
        text = f"Invited to group {self.group_id} by {self.inviter_uin or self.inviter_uid}"
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

    operator_uid: Optional[str] = None
    operator_uin: int
    action: str
    suffix: str
    action_image: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.operator_uin or self.operator_uid} send nudge"
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

    operator_uid: Optional[str] = None
    operator_uin: int
    message_id: str
    tip_text: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.operator_uin or self.operator_uid} recall message {self.message_id}"
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

    target_uid: Optional[str] = None
    target_uin: int
    title: str
    group_id: int

    @override
    def get_event_description(self) -> str:
        text = f"{self.target_uin}'s unique title in Group {self.group_id} changed to {self.title}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target_uin}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target_uin}"


class GroupEssenceMessageNotice(NoticeEvent):
    __type__: Literal["group_essence_changed"] = "group_essence_changed"

    group_id: int
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int
    message_id: str
    sub_type: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} essence message {self.message_id} changed by {self.operator_uin or self.operator_uid}"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int
    action: str
    suffix: str
    action_image: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uin or self.operator_uid} send nudge"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int
    new_card: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uin or self.operator_uid} change {self.target_uin or self.target_uid}'s card to {self.new_card}"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int

    flag: GroupMemberIncreasedNoticeGroupMemberIncreasedType = Field(
        GroupMemberIncreasedNoticeGroupMemberIncreasedType.UNSPECIFIED, alias="type"
    )

    @field_validator("flag", mode="before")
    def check_flag(cls, v):
        if v is None:
            return GroupMemberIncreasedNoticeGroupMemberIncreasedType.APPROVE
        if isinstance(v, GroupMemberIncreasedNoticeGroupMemberIncreasedType):
            return v
        if isinstance(v, int):
            return GroupMemberIncreasedNoticeGroupMemberIncreasedType(v)
        if isinstance(v, str) and v.upper() in GroupMemberIncreasedNoticeGroupMemberIncreasedType.__members__:
            return GroupMemberIncreasedNoticeGroupMemberIncreasedType.__members__[v.upper()]
        raise ValueError(f"invalid flag: {v}")

    @override
    def get_event_description(self) -> str:
        text = f"New member {self.target_uin or self.target_uid} joined Group {self.group_id} by {self.operator_uin or self.operator_uid}"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int

    flag: GroupMemberDecreasedNoticeGroupMemberDecreasedType = Field(
        GroupMemberDecreasedNoticeGroupMemberDecreasedType.UNSPECIFIED, alias="type"
    )

    @field_validator("flag", mode="before")
    def check_flag(cls, v):
        if v is None:
            return GroupMemberDecreasedNoticeGroupMemberDecreasedType.LEAVE
        if isinstance(v, GroupMemberDecreasedNoticeGroupMemberDecreasedType):
            return v
        if isinstance(v, int):
            return GroupMemberDecreasedNoticeGroupMemberDecreasedType(v)
        if isinstance(v, str) and v.upper() in GroupMemberDecreasedNoticeGroupMemberDecreasedType.__members__:
            return GroupMemberDecreasedNoticeGroupMemberDecreasedType.__members__[v.upper()]
        raise ValueError(f"invalid flag: {v}")

    @override
    def get_event_description(self) -> str:
        text = f"Member {self.target_uin or self.target_uid} left Group {self.group_id} by {self.operator_uin or self.operator_uid}"
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
    target_uid: Optional[str] = None
    target_uin: int
    is_admin: bool

    @override
    def get_event_description(self) -> str:
        text = (
            f"Group {self.group_id} {self.target_uin or self.target_uid} become admin"
            if self.is_admin
            else f"Group {self.group_id} {self.target_uin or self.target_uid} lose admin"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int
    duration: int

    flag: GroupMemberBanNoticeGroupMemberBanType = Field(
        GroupMemberBanNoticeGroupMemberBanType.UNSPECIFIED, alias="type"
    )

    @field_validator("flag", mode="before")
    def check_flag(cls, v):
        if v is None:
            return GroupMemberBanNoticeGroupMemberBanType.LIFT_BAN
        if isinstance(v, GroupMemberBanNoticeGroupMemberBanType):
            return v
        if isinstance(v, int):
            return GroupMemberBanNoticeGroupMemberBanType(v)
        if isinstance(v, str) and v.upper() in GroupMemberBanNoticeGroupMemberBanType.__members__:
            return GroupMemberBanNoticeGroupMemberBanType.__members__[v.upper()]
        raise ValueError(f"invalid flag: {v}")

    @override
    def get_event_description(self) -> str:
        text = (
            (
                f"Group {self.group_id} {self.target_uin or self.target_uid} banned by {self.operator_uin or self.operator_uid}"
            )
            if self.duration
            else (
                f"Group {self.group_id} {self.target_uin or self.target_uid} unbanned by {self.operator_uin or self.operator_uid}"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uin or self.operator_uid} recall message {self.message_id}"
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
    target_uid: Optional[str] = None
    target_uin: int
    action: str
    rank_image: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.target_uin or self.target_uid} sign in"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    is_ban: bool

    @override
    def get_event_description(self) -> str:
        text = (
            f"Group {self.group_id} whole banned by {self.operator_uin or self.operator_uid} "
            if self.is_ban
            else f"Group {self.group_id} whole unbanned by {self.operator_uin or self.operator_uid}"
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


class GroupTransferNotice(NoticeEvent):
    __type__: Literal["group_transfer"] = "group_transfer"

    group_id: int
    operator_uid: Optional[str] = None
    operator_uin: int
    target_uid: Optional[str] = None
    target_uin: int

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} transfer to {self.target_uin or self.target_uid} by {self.operator_uin or self.operator_uid}"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.target_uin or self.target_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.group_id}_{self.target_uin or self.target_uid}"


class FriendIncreaseNotice(NoticeEvent):
    __type__: Literal["friend_increase"] = "friend_increase"

    friend_uid: Optional[str] = None
    friend_uin: int
    friend_nick: Optional[str]

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.friend_nick or ''}({self.friend_uin or self.friend_uid}) added you"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.friend_uin or self.friend_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.friend_uin or self.friend_uid}"

    @override
    def is_tome(self) -> bool:
        return True


class FriendDecreaseNotice(NoticeEvent):
    __type__: Literal["friend_decrease"] = "friend_decrease"

    friend_uid: Optional[str] = None
    friend_uin: int
    friend_nick: Optional[str]

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.friend_nick or ''}({self.friend_uin or self.friend_uid}) removed you"
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return f"{self.friend_uin or self.friend_uid}"

    @override
    def get_session_id(self) -> str:
        return f"{self.friend_uin or self.friend_uid}"

    @override
    def is_tome(self) -> bool:
        return True


class PrivateFileUploadedNotice(NoticeEvent):
    __type__: Literal["private_file_uploaded"] = "private_file_uploaded"

    operator_uid: Optional[str] = None
    operator_uin: int
    file_id: str
    file_sub_id: int
    file_name: str
    file_size: int
    expire_time: datetime
    file_url: str

    @override
    def get_event_description(self) -> str:
        text = f"Friend {self.operator_uin or self.operator_uid} uploaded file {self.file_name}"
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
    operator_uid: Optional[str] = None
    operator_uin: int
    file_id: str
    file_sub_id: int
    file_name: str
    file_size: int
    expire_time: datetime
    file_url: str

    @override
    def get_event_description(self) -> str:
        text = f"Group {self.group_id} {self.operator_uin or self.operator_uid} uploaded file {self.file_name}"
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
