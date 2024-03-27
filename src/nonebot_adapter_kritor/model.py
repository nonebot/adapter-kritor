from enum import IntEnum
from typing import Optional, Literal, Union

from pydantic import BaseModel, Field

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

class Sender(BaseModel):
    uid: str
    uin: Optional[int] = None
    nick: Optional[str] = None
