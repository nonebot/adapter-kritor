from enum import IntEnum
from typing import Optional
from dataclasses import dataclass

from pydantic import BaseModel

from .compat import field_validator
from .protos.kritor.common import Role as ProtoRole
from .protos.kritor.common import Scene as ProtoScene
from .protos.kritor.common import Contact as ProtoContact
from .protos.kritor.common import GroupSender as ProtoGroupSender
from .protos.kritor.common import GuildSender as ProtoGuildSender
from .protos.kritor.common import PrivateSender as ProtoPrivateSender


class SceneType(IntEnum):
    UNSPECIFIED = 0
    GROUP = 1
    FRIEND = 2
    GUILD = 3
    STRANGER_FROM_GROUP = 11
    NEARBY = 6
    """以下类型为可选实现"""

    STRANGER = 10


@dataclass
class Contact:
    type: SceneType
    id: str
    sub_id: Optional[str] = None

    def dump(self) -> ProtoContact:
        return ProtoContact(
            scene=ProtoScene(self.type.value),
            peer=self.id,
            sub_peer=self.sub_id,
        )


class Role(IntEnum):
    UNKNOWN = 0
    MEMBER = 1
    ADMIN = 2
    OWNER = 3


class PrivateSender(BaseModel):
    uid: Optional[str] = None
    uin: int
    nick: str

    def dump(self) -> ProtoPrivateSender:
        return ProtoPrivateSender(
            uid=self.uid,
            uin=self.uin,
            nick=self.nick,
        )


class GroupSender(BaseModel):
    group_id: str
    uid: Optional[str] = None
    uin: int
    nick: str

    def dump(self) -> ProtoGroupSender:
        return ProtoGroupSender(
            group_id=self.group_id,
            uid=self.uid,
            uin=self.uin,
            nick=self.nick,
        )


class GuildSender(BaseModel):
    guild_id: str
    channel_id: str
    tiny_id: str
    nick: str
    role: Role

    @field_validator("role", mode="before")
    def check_role(cls, v):
        if v is None:
            return Role.UNKNOWN
        if isinstance(v, Role):
            return v
        if isinstance(v, int):
            return Role(v)
        if isinstance(v, ProtoRole):
            return Role(v.value)
        if isinstance(v, str) and v.upper() in Role.__members__:
            return Role.__members__[v.upper()]
        raise ValueError(f"invalid role: {v}")

    def dump(self) -> ProtoGuildSender:
        return ProtoGuildSender(
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            tiny_id=self.tiny_id,
            nick=self.nick,
            role=ProtoRole(self.role.value),
        )
