# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: event/event.proto, event/event_notice.proto, event/event_request.proto, event/notice_data.proto, event/request_data.proto
# plugin: python-betterproto
# This file has been @generated

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Union, Iterable, Optional, AsyncIterable, AsyncIterator

import grpclib
import betterproto
from betterproto.grpc.grpclib_server import ServiceBase

from .. import common as _common__

if TYPE_CHECKING:
    import grpclib.server
    from grpclib.metadata import Deadline
    from betterproto.grpc.grpclib_client import MetadataLike


class GroupMemberIncreasedNoticeGroupMemberIncreasedType(betterproto.Enum):
    APPROVE = 0
    INVITE = 1


class GroupMemberDecreasedNoticeGroupMemberDecreasedType(betterproto.Enum):
    LEAVE = 0
    KICK = 1
    KICK_ME = 2


class GroupMemberBanNoticeGroupMemberBanType(betterproto.Enum):
    LIFT_BAN = 0
    BAN = 1


class NoticeEventNoticeType(betterproto.Enum):
    UNKNOWN = 0
    FRIEND_POKE = 10
    FRIEND_RECALL = 11
    FRIEND_FILE_COME = 12
    GROUP_POKE = 20
    GROUP_CARD_CHANGED = 21
    GROUP_MEMBER_UNIQUE_TITLE_CHANGED = 22
    GROUP_ESSENCE_CHANGED = 23
    GROUP_RECALL = 24
    GROUP_MEMBER_INCREASE = 25
    GROUP_MEMBER_DECREASE = 26
    GROUP_ADMIN_CHANGED = 27
    GROUP_MEMBER_BANNED = 28
    GROUP_SIGN = 29
    GROUP_WHOLE_BAN = 30
    GROUP_FILE_COME = 31


class RequestsEventRequestType(betterproto.Enum):
    FRIEND_APPLY = 0
    GROUP_APPLY = 1
    INVITED_GROUP = 2


class EventType(betterproto.Enum):
    EVENT_TYPE_CORE_EVENT = 0
    EVENT_TYPE_MESSAGE = 1
    EVENT_TYPE_NOTICE = 2
    EVENT_TYPE_REQUEST = 3


@dataclass(eq=False, repr=False)
class FriendPokeNotice(betterproto.Message):
    operator_uid: str = betterproto.string_field(1)
    operator_uin: int = betterproto.uint64_field(2)
    action: str = betterproto.string_field(3)
    suffix: str = betterproto.string_field(4)
    action_image: str = betterproto.string_field(5)


@dataclass(eq=False, repr=False)
class FriendRecallNotice(betterproto.Message):
    operator_uid: str = betterproto.string_field(1)
    operator_uin: int = betterproto.uint64_field(2)
    message_id: str = betterproto.string_field(3)
    tip_text: str = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class GroupUniqueTitleChangedNotice(betterproto.Message):
    target: int = betterproto.uint64_field(1)
    title: str = betterproto.string_field(2)
    group_id: int = betterproto.uint64_field(3)


@dataclass(eq=False, repr=False)
class GroupEssenceMessageNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: str = betterproto.string_field(2)
    operator_uin: int = betterproto.uint64_field(3)
    target_uid: str = betterproto.string_field(4)
    target_uin: int = betterproto.uint64_field(5)
    message_id: str = betterproto.string_field(6)
    sub_type: int = betterproto.uint32_field(7)


@dataclass(eq=False, repr=False)
class GroupPokeNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: str = betterproto.string_field(2)
    operator_uin: int = betterproto.uint64_field(3)
    target_uid: str = betterproto.string_field(4)
    target_uin: int = betterproto.uint64_field(5)
    action: str = betterproto.string_field(6)
    suffix: str = betterproto.string_field(7)
    action_image: str = betterproto.string_field(8)


@dataclass(eq=False, repr=False)
class GroupCardChangedNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: str = betterproto.string_field(2)
    operator_uin: int = betterproto.uint64_field(3)
    target_uid: str = betterproto.string_field(4)
    target_uin: int = betterproto.uint64_field(5)
    new_card: str = betterproto.string_field(6)


@dataclass(eq=False, repr=False)
class GroupMemberIncreasedNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: str = betterproto.string_field(2)
    operator_uin: int = betterproto.uint64_field(3)
    target_uid: str = betterproto.string_field(4)
    target_uin: int = betterproto.uint64_field(5)
    type: "GroupMemberIncreasedNoticeGroupMemberIncreasedType" = betterproto.enum_field(6)


@dataclass(eq=False, repr=False)
class GroupMemberDecreasedNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: Optional[str] = betterproto.string_field(2, optional=True, group="_operator_uid")
    operator_uin: Optional[int] = betterproto.uint64_field(3, optional=True, group="_operator_uin")
    target_uid: Optional[str] = betterproto.string_field(4, optional=True, group="_target_uid")
    target_uin: Optional[int] = betterproto.uint64_field(5, optional=True, group="_target_uin")
    type: "GroupMemberDecreasedNoticeGroupMemberDecreasedType" = betterproto.enum_field(6)


@dataclass(eq=False, repr=False)
class GroupAdminChangedNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    target_uid: str = betterproto.string_field(4)
    target_uin: int = betterproto.uint64_field(5)
    is_admin: bool = betterproto.bool_field(6)


@dataclass(eq=False, repr=False)
class GroupMemberBanNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: str = betterproto.string_field(2)
    operator_uin: int = betterproto.uint64_field(3)
    target_uid: str = betterproto.string_field(4)
    target_uin: int = betterproto.uint64_field(5)
    duration: int = betterproto.int32_field(6)
    type: "GroupMemberBanNoticeGroupMemberBanType" = betterproto.enum_field(7)


@dataclass(eq=False, repr=False)
class GroupRecallNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    message_id: str = betterproto.string_field(2)
    tip_text: str = betterproto.string_field(3)
    operator_uid: str = betterproto.string_field(4)
    operator_uin: int = betterproto.uint64_field(5)
    target_uid: str = betterproto.string_field(6)
    target_uin: int = betterproto.uint64_field(7)
    message_seq: int = betterproto.uint64_field(8)


@dataclass(eq=False, repr=False)
class GroupSignInNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    target_uid: str = betterproto.string_field(2)
    target_uin: int = betterproto.uint64_field(3)
    action: str = betterproto.string_field(4)
    suffix: str = betterproto.string_field(5)
    rank_image: str = betterproto.string_field(6)


@dataclass(eq=False, repr=False)
class GroupWholeBanNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: str = betterproto.string_field(2)
    operator_uin: int = betterproto.uint64_field(3)
    is_ban: bool = betterproto.bool_field(4)


@dataclass(eq=False, repr=False)
class FriendFileUploadedNotice(betterproto.Message):
    operator_uid: str = betterproto.string_field(1)
    operator_uin: int = betterproto.uint64_field(2)
    file_id: str = betterproto.string_field(3)
    file_sub_id: str = betterproto.string_field(4)
    file_name: str = betterproto.string_field(5)
    file_size: int = betterproto.uint64_field(6)
    expire_time: int = betterproto.uint32_field(7)
    url: str = betterproto.string_field(8)


@dataclass(eq=False, repr=False)
class GroupFileUploadedNotice(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    operator_uid: str = betterproto.string_field(2)
    operator_uin: int = betterproto.uint64_field(3)
    file_id: str = betterproto.string_field(4)
    file_sub_id: str = betterproto.string_field(5)
    file_name: str = betterproto.string_field(6)
    file_size: int = betterproto.uint64_field(7)
    expire_time: int = betterproto.uint32_field(8)
    biz: int = betterproto.int32_field(9)
    url: str = betterproto.string_field(10)


@dataclass(eq=False, repr=False)
class NoticeEvent(betterproto.Message):
    type: "NoticeEventNoticeType" = betterproto.enum_field(1)
    time: int = betterproto.uint32_field(2)
    friend_poke: "FriendPokeNotice" = betterproto.message_field(10, group="notice")
    friend_recall: "FriendRecallNotice" = betterproto.message_field(11, group="notice")
    friend_file_uploaded: "FriendFileUploadedNotice" = betterproto.message_field(12, group="notice")
    group_poke: "GroupPokeNotice" = betterproto.message_field(20, group="notice")
    group_card_changed: "GroupCardChangedNotice" = betterproto.message_field(21, group="notice")
    group_member_unique_title_changed: "GroupUniqueTitleChangedNotice" = betterproto.message_field(22, group="notice")
    group_essence_changed: "GroupEssenceMessageNotice" = betterproto.message_field(23, group="notice")
    group_recall: "GroupRecallNotice" = betterproto.message_field(24, group="notice")
    group_member_increase: "GroupMemberIncreasedNotice" = betterproto.message_field(25, group="notice")
    group_member_decrease: "GroupMemberDecreasedNotice" = betterproto.message_field(26, group="notice")
    group_admin_change: "GroupAdminChangedNotice" = betterproto.message_field(27, group="notice")
    group_member_ban: "GroupMemberBanNotice" = betterproto.message_field(28, group="notice")
    group_sign_in: "GroupSignInNotice" = betterproto.message_field(29, group="notice")
    group_whole_ban: "GroupWholeBanNotice" = betterproto.message_field(30, group="notice")
    group_file_uploaded: "GroupFileUploadedNotice" = betterproto.message_field(31, group="notice")


@dataclass(eq=False, repr=False)
class FriendApplyRequest(betterproto.Message):
    applier_uid: str = betterproto.string_field(1)
    applier_uin: int = betterproto.uint64_field(2)
    flag: str = betterproto.string_field(3)
    message: str = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class GroupApplyRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    applier_uid: str = betterproto.string_field(2)
    applier_uin: int = betterproto.uint64_field(3)
    inviter_uid: str = betterproto.string_field(4)
    inviter_uin: int = betterproto.uint64_field(5)
    reason: str = betterproto.string_field(6)
    flag: str = betterproto.string_field(7)


@dataclass(eq=False, repr=False)
class InvitedJoinGroupRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    inviter_uid: str = betterproto.string_field(2)
    inviter_uin: int = betterproto.uint64_field(3)
    flag: str = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class RequestsEvent(betterproto.Message):
    type: "RequestsEventRequestType" = betterproto.enum_field(1)
    time: int = betterproto.uint32_field(2)
    friend_apply: "FriendApplyRequest" = betterproto.message_field(3, group="request")
    group_apply: "GroupApplyRequest" = betterproto.message_field(4, group="request")
    invited_group: "InvitedJoinGroupRequest" = betterproto.message_field(5, group="request")


@dataclass(eq=False, repr=False)
class RequestPushEvent(betterproto.Message):
    type: "EventType" = betterproto.enum_field(1)


@dataclass(eq=False, repr=False)
class EventStructure(betterproto.Message):
    type: "EventType" = betterproto.enum_field(1)
    message: "_common__.PushMessageBody" = betterproto.message_field(2, group="event")
    request: "RequestsEvent" = betterproto.message_field(3, group="event")
    notice: "NoticeEvent" = betterproto.message_field(4, group="event")


class EventServiceStub(betterproto.ServiceStub):
    async def register_active_listener(
        self,
        request_push_event: "RequestPushEvent",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> AsyncIterator["EventStructure"]:
        async for response in self._unary_stream(
            "/kritor.event.EventService/RegisterActiveListener",
            request_push_event,
            EventStructure,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ):
            yield response

    async def register_passive_listener(
        self,
        event_structure_iterator: Union[AsyncIterable["EventStructure"], Iterable["EventStructure"]],
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "RequestPushEvent":
        return await self._stream_unary(
            "/kritor.event.EventService/RegisterPassiveListener",
            event_structure_iterator,
            EventStructure,
            RequestPushEvent,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class EventServiceBase(ServiceBase):

    async def register_active_listener(self, request_push_event: "RequestPushEvent") -> AsyncIterator["EventStructure"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)
        yield EventStructure()

    async def register_passive_listener(
        self, event_structure_iterator: AsyncIterator["EventStructure"]
    ) -> "RequestPushEvent":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_register_active_listener(
        self, stream: "grpclib.server.Stream[RequestPushEvent, EventStructure]"
    ) -> None:
        request = await stream.recv_message()
        await self._call_rpc_handler_server_stream(
            self.register_active_listener,
            stream,
            request,
        )

    async def __rpc_register_passive_listener(
        self, stream: "grpclib.server.Stream[EventStructure, RequestPushEvent]"
    ) -> None:
        request = stream.__aiter__()
        response = await self.register_passive_listener(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/kritor.event.EventService/RegisterActiveListener": grpclib.const.Handler(
                self.__rpc_register_active_listener,
                grpclib.const.Cardinality.UNARY_STREAM,
                RequestPushEvent,
                EventStructure,
            ),
            "/kritor.event.EventService/RegisterPassiveListener": grpclib.const.Handler(
                self.__rpc_register_passive_listener,
                grpclib.const.Cardinality.STREAM_UNARY,
                EventStructure,
                RequestPushEvent,
            ),
        }
