from enum import IntEnum
from typing import Union, Literal, Optional

from pydantic import Field, BaseModel

from .protos.kritor.common import Scene
from .protos.kritor.common import Role as ProtoRole
from .protos.kritor.common import Sender as ProtoSender
from .protos.kritor.common import Contact as ProtoContact


class SceneType(IntEnum):
    GROUP = 0
    FRIEND = 1
    GUILD = 2
    STRANGER_FROM_GROUP = 10
    NEARBY = 5
    """以下类型为可选实现"""

    STRANGER = 9


class Contact(BaseModel):
    type: SceneType = Field(..., alias="scene")
    id: str = Field(..., alias="peer")
    sub_id: Optional[str] = Field(None, alias="sub_peer")

    def dump(self) -> ProtoContact:
        return ProtoContact(
            scene=Scene(self.type.value),
            peer=self.id,
            sub_peer=self.sub_id,
        )


class Group(Contact):
    type: Literal[SceneType.GROUP] = SceneType.GROUP


class Friend(Contact):
    type: Literal[SceneType.FRIEND] = SceneType.FRIEND


class Guild(Contact):
    type: Literal[SceneType.GUILD] = SceneType.GUILD


class Stranger(Contact):
    type: Literal[SceneType.STRANGER] = SceneType.STRANGER


class StrangerFromGroup(Contact):
    type: Literal[SceneType.STRANGER_FROM_GROUP] = SceneType.STRANGER_FROM_GROUP


class Nearby(Contact):
    type: Literal[SceneType.NEARBY] = SceneType.NEARBY


ContactType = Union[
    Union[Group, Friend, Guild, Stranger, StrangerFromGroup, Nearby],
    Contact,
]


class Role(IntEnum):
    UNKNOWN = 0
    MEMBER = 1
    ADMIN = 2
    OWNER = 3


class Sender(BaseModel):
    uid: str
    uin: Optional[int] = None
    nick: Optional[str] = None
    role: Optional[Role] = None

    def dump(self) -> ProtoSender:
        return ProtoSender(
            uid=self.uid,
            uin=self.uin,
            nick=self.nick,
            role=ProtoRole(self.role.value) if self.role else None,
        )
