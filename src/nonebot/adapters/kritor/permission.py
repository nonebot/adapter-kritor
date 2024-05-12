from nonebot.permission import Permission

from .model import Role
from .event import TempMessage, GroupMessage, MessageEvent, FriendMessage, StrangerMessage


async def _private(event: MessageEvent) -> bool:
    return isinstance(event, (FriendMessage, TempMessage, StrangerMessage))


async def _private_friend(event: FriendMessage) -> bool:
    return True


async def _private_temp(event: TempMessage) -> bool:
    return True


async def _private_other(event: StrangerMessage) -> bool:
    return True


PRIVATE: Permission = Permission(_private)
""" 匹配任意私聊消息类型事件"""
P_FRIEND: Permission = Permission(_private_friend)
"""匹配任意好友私聊消息类型事件"""
P_TEMP: Permission = Permission(_private_temp)
"""匹配任意群临时私聊消息类型事件"""
P_STRANGER: Permission = Permission(_private_other)
"""匹配任意陌生人私聊消息类型事件"""


async def _group(event: GroupMessage) -> bool:
    return True


async def _group_member(event: GroupMessage) -> bool:
    if not event.sender.role:
        return True
    return event.sender.role is Role.UNKNOWN


async def _group_admin(event: GroupMessage) -> bool:
    if not event.sender.role:
        return True
    return event.sender.role is Role.ADMIN


async def _group_owner(event: GroupMessage) -> bool:
    if not event.sender.role:
        return True
    return event.sender.role is Role.OWNER


GROUP: Permission = Permission(_group)
"""匹配任意群聊消息类型事件"""
GROUP_MEMBER: Permission = Permission(_group_member)
"""匹配任意群员群聊消息类型事件

:::warning 警告
该权限通过 event.sender 进行判断且不包含管理员以及群主！
:::
"""
GROUP_ADMIN: Permission = Permission(_group_admin)
"""匹配任意群管理员群聊消息类型事件"""
GROUP_OWNER: Permission = Permission(_group_owner)
"""匹配任意群主群聊消息类型事件"""

__all__ = [
    "PRIVATE",
    "P_FRIEND",
    "P_TEMP",
    "P_STRANGER",
    "GROUP",
    "GROUP_MEMBER",
    "GROUP_ADMIN",
    "GROUP_OWNER",
]
