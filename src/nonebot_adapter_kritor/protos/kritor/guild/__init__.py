# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: guild/guild.proto, guild/guild_data.proto
# plugin: python-betterproto
# This file has been @generated

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
)

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


@dataclass(eq=False, repr=False)
class GuildInfo(betterproto.Message):
    """频道信息"""

    guild_id: int = betterproto.uint64_field(1)
    guild_name: str = betterproto.string_field(2)
    guild_display_id: str = betterproto.string_field(3)
    profile: str = betterproto.string_field(4)
    is_enable: bool = betterproto.bool_field(5)
    is_banned: bool = betterproto.bool_field(6)
    is_frozen: bool = betterproto.bool_field(7)
    owner_id: int = betterproto.uint64_field(8)
    shutup_expire_time: int = betterproto.uint64_field(9)
    allow_search: bool = betterproto.bool_field(10)


@dataclass(eq=False, repr=False)
class ChannelInfo(betterproto.Message):
    """子频道信息"""

    channel_id: int = betterproto.uint64_field(1)
    guild_id: int = betterproto.uint64_field(2)
    channel_name: str = betterproto.string_field(3)
    create_time: int = betterproto.uint64_field(4)
    max_member_count: int = betterproto.uint64_field(5)
    creator_tiny_id: int = betterproto.uint64_field(6)
    talk_permission: int = betterproto.uint64_field(7)
    visible_type: int = betterproto.uint64_field(8)
    current_slow_mode: int = betterproto.uint64_field(9)
    slow_modes: List["SlowModes"] = betterproto.message_field(10)
    icon_url: str = betterproto.string_field(11)
    jump_switch: int = betterproto.uint64_field(12)
    jump_type: int = betterproto.uint64_field(13)
    jump_url: str = betterproto.string_field(14)
    category_id: int = betterproto.uint64_field(15)
    my_talk_permission: int = betterproto.uint64_field(16)


@dataclass(eq=False, repr=False)
class SlowModes(betterproto.Message):
    """发言限制"""

    slow_mode_key: int = betterproto.uint64_field(1)
    slow_mode_text: str = betterproto.string_field(2)
    speak_frequency: int = betterproto.uint64_field(3)
    slow_mode_circle: int = betterproto.uint64_field(4)


@dataclass(eq=False, repr=False)
class MemberInfo(betterproto.Message):
    """频道成员信息"""

    tiny_id: int = betterproto.uint64_field(1)
    title: str = betterproto.string_field(2)
    nickname: str = betterproto.string_field(3)
    role_id: int = betterproto.uint64_field(4)
    role_name: str = betterproto.string_field(5)
    role_color: int = betterproto.uint64_field(6)
    join_time: int = betterproto.uint64_field(7)
    robot_type: int = betterproto.uint64_field(8)
    type: int = betterproto.uint64_field(9)
    in_black: bool = betterproto.bool_field(10)
    platform: int = betterproto.uint64_field(11)


@dataclass(eq=False, repr=False)
class MemberProfile(betterproto.Message):
    """频道成员资料"""

    tiny_id: int = betterproto.uint64_field(1)
    nickname: str = betterproto.string_field(2)
    avatar_url: str = betterproto.string_field(3)
    join_time: int = betterproto.uint64_field(4)
    roles_info: List["MemberRoleInfo"] = betterproto.message_field(5)


@dataclass(eq=False, repr=False)
class PermissionInfo(betterproto.Message):
    """身份组权限信息"""

    root_id: int = betterproto.uint64_field(1)
    child_ids: List[int] = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class MemberRoleInfo(betterproto.Message):
    """用户身份组信息"""

    role_id: int = betterproto.uint64_field(1)
    role_name: str = betterproto.string_field(2)
    color: int = betterproto.uint64_field(3)
    permissions: List["PermissionInfo"] = betterproto.message_field(4)
    type: int = betterproto.uint64_field(5)
    display_name: str = betterproto.string_field(6)


@dataclass(eq=False, repr=False)
class RoleInfo(betterproto.Message):
    """频道身份组详细信息"""

    role_id: int = betterproto.uint64_field(1)
    role_name: str = betterproto.string_field(2)
    color: int = betterproto.uint64_field(3)
    permissions: List["PermissionInfo"] = betterproto.message_field(4)
    disabled: bool = betterproto.bool_field(5)
    independent: bool = betterproto.bool_field(6)
    max_count: int = betterproto.uint64_field(7)
    member_count: int = betterproto.uint64_field(8)
    owned: bool = betterproto.bool_field(9)


@dataclass(eq=False, repr=False)
class GetBotInfoRequest(betterproto.Message):
    """获取BOT资料请求"""

    pass


@dataclass(eq=False, repr=False)
class GetBotInfoResponse(betterproto.Message):
    """获取BOT资料响应"""

    nickname: str = betterproto.string_field(1)
    tiny_id: int = betterproto.uint64_field(2)
    avatar: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class GetChannelListRequest(betterproto.Message):
    """获取频道列表请求"""

    pass


@dataclass(eq=False, repr=False)
class GetChannelListResponse(betterproto.Message):
    """获取频道列表响应"""

    get_guild_list: List["GuildInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class GetGuildMetaByGuestRequest(betterproto.Message):
    """通过访客获取频道元数据请求"""

    guild_id: int = betterproto.uint64_field(1)


@dataclass(eq=False, repr=False)
class GetGuildMetaByGuestResponse(betterproto.Message):
    """通过访客获取频道元数据响应"""

    guild_id: int = betterproto.uint64_field(1)
    guild_name: str = betterproto.string_field(2)
    guild_profile: str = betterproto.string_field(3)
    create_time: int = betterproto.uint64_field(4)
    max_member_count: int = betterproto.uint64_field(5)
    max_robot_count: int = betterproto.uint64_field(6)
    max_admin_count: int = betterproto.uint64_field(7)
    member_count: int = betterproto.uint64_field(8)
    owner_id: int = betterproto.uint64_field(9)
    guild_display_id: str = betterproto.string_field(10)


@dataclass(eq=False, repr=False)
class GetGuildChannelListRequest(betterproto.Message):
    """获取子频道列表请求"""

    guild_id: int = betterproto.uint64_field(1)
    refresh: bool = betterproto.bool_field(2)


@dataclass(eq=False, repr=False)
class GetGuildChannelListResponse(betterproto.Message):
    """获取子频道列表响应"""

    channels_info: List["ChannelInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class GetGuildMemberListRequest(betterproto.Message):
    """获取频道成员列表请求"""

    guild_id: int = betterproto.uint64_field(1)
    next_token: str = betterproto.string_field(2)
    all: bool = betterproto.bool_field(3)
    refresh: bool = betterproto.bool_field(4)


@dataclass(eq=False, repr=False)
class GetGuildMemberListResponse(betterproto.Message):
    """获取频道成员列表响应"""

    members_info: List["MemberInfo"] = betterproto.message_field(1)
    next_token: str = betterproto.string_field(2)
    finished: bool = betterproto.bool_field(3)


@dataclass(eq=False, repr=False)
class GetGuildMemberRequest(betterproto.Message):
    """单独获取频道成员资料请求"""

    guild_id: int = betterproto.uint64_field(1)
    tiny_id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class GetGuildMemberResponse(betterproto.Message):
    """单独获取频道成员资料响应"""

    member_info: "MemberProfile" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class SendChannelMessageRequest(betterproto.Message):
    """发送信息到子频道请求"""

    guild_id: int = betterproto.uint64_field(1)
    channel_id: int = betterproto.uint64_field(2)
    message: str = betterproto.string_field(3)
    retry_cnt: int = betterproto.int32_field(4)
    recall_duration: int = betterproto.int64_field(5)


@dataclass(eq=False, repr=False)
class SendChannelMessageResponse(betterproto.Message):
    """发送信息到子频道响应"""

    message_id: str = betterproto.string_field(1)
    time: int = betterproto.int64_field(2)


@dataclass(eq=False, repr=False)
class GetGuildFeedListRequest(betterproto.Message):
    """获取频道帖子广场帖子请求"""

    guild_id: int = betterproto.uint64_field(1)
    from_: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class GetGuildFeedListResponse(betterproto.Message):
    """获取频道帖子广场帖子响应"""

    data: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class GetGuildRoleListRequest(betterproto.Message):
    """获取频道角色列表请求"""

    guild_id: int = betterproto.uint64_field(1)


@dataclass(eq=False, repr=False)
class GetGuildRoleListResponse(betterproto.Message):
    """获取频道角色列表响应"""

    roles_info: List["RoleInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class DeleteGuildRoleRequest(betterproto.Message):
    """删除频道身份组请求"""

    guild_id: int = betterproto.uint64_field(1)
    role_id: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class DeleteGuildRoleResponse(betterproto.Message):
    """删除频道身份组响应"""

    pass


@dataclass(eq=False, repr=False)
class SetGuildMemberRoleRequest(betterproto.Message):
    """设置用户在频道中的角色"""

    guild_id: int = betterproto.uint64_field(1)
    role_id: int = betterproto.uint64_field(2)
    set: bool = betterproto.bool_field(3)
    tiny_ids: List[str] = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class SetGuildMemberRoleResponse(betterproto.Message):
    """设置用户在频道中的角色响应"""

    pass


@dataclass(eq=False, repr=False)
class UpdateGuildRoleRequest(betterproto.Message):
    """修改频道角色请求"""

    guild_id: int = betterproto.uint64_field(1)
    role_id: int = betterproto.uint64_field(2)
    name: str = betterproto.string_field(3)
    color: int = betterproto.int64_field(4)


@dataclass(eq=False, repr=False)
class UpdateGuildRoleResponse(betterproto.Message):
    """修改频道角色响应"""

    pass


@dataclass(eq=False, repr=False)
class CreateGuildRoleRequest(betterproto.Message):
    """创建频道角色请求"""

    guild_id: int = betterproto.uint64_field(1)
    name: str = betterproto.string_field(2)
    color: int = betterproto.int64_field(3)


@dataclass(eq=False, repr=False)
class CreateGuildRoleResponse(betterproto.Message):
    """创建频道角色响应"""

    role_id: int = betterproto.uint64_field(1)


class GuildServiceStub(betterproto.ServiceStub):
    async def get_bot_info(
        self,
        get_bot_info_request: "GetBotInfoRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetBotInfoResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetBotInfo",
            get_bot_info_request,
            GetBotInfoResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_channel_list(
        self,
        get_channel_list_request: "GetChannelListRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetChannelListResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetChannelList",
            get_channel_list_request,
            GetChannelListResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_guild_meta_by_guest(
        self,
        get_guild_meta_by_guest_request: "GetGuildMetaByGuestRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetGuildMetaByGuestResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetGuildMetaByGuest",
            get_guild_meta_by_guest_request,
            GetGuildMetaByGuestResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_guild_channel_list(
        self,
        get_guild_channel_list_request: "GetGuildChannelListRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetGuildChannelListResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetGuildChannelList",
            get_guild_channel_list_request,
            GetGuildChannelListResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_guild_member_list(
        self,
        get_guild_member_list_request: "GetGuildMemberListRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetGuildMemberListResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetGuildMemberList",
            get_guild_member_list_request,
            GetGuildMemberListResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_guild_member(
        self,
        get_guild_member_request: "GetGuildMemberRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetGuildMemberResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetGuildMember",
            get_guild_member_request,
            GetGuildMemberResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def send_channel_message(
        self,
        send_channel_message_request: "SendChannelMessageRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SendChannelMessageResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/SendChannelMessage",
            send_channel_message_request,
            SendChannelMessageResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_guild_feed_list(
        self,
        get_guild_feed_list_request: "GetGuildFeedListRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetGuildFeedListResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetGuildFeedList",
            get_guild_feed_list_request,
            GetGuildFeedListResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_guild_role_list(
        self,
        get_guild_role_list_request: "GetGuildRoleListRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetGuildRoleListResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/GetGuildRoleList",
            get_guild_role_list_request,
            GetGuildRoleListResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def delete_guild_role(
        self,
        delete_guild_role_request: "DeleteGuildRoleRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "DeleteGuildRoleResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/DeleteGuildRole",
            delete_guild_role_request,
            DeleteGuildRoleResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def set_guild_member_role(
        self,
        set_guild_member_role_request: "SetGuildMemberRoleRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SetGuildMemberRoleResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/SetGuildMemberRole",
            set_guild_member_role_request,
            SetGuildMemberRoleResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def update_guild_role(
        self,
        update_guild_role_request: "UpdateGuildRoleRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "UpdateGuildRoleResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/UpdateGuildRole",
            update_guild_role_request,
            UpdateGuildRoleResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def create_guild_role(
        self,
        create_guild_role_request: "CreateGuildRoleRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "CreateGuildRoleResponse":
        return await self._unary_unary(
            "/kritor.guild.GuildService/CreateGuildRole",
            create_guild_role_request,
            CreateGuildRoleResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class GuildServiceBase(ServiceBase):

    async def get_bot_info(
        self, get_bot_info_request: "GetBotInfoRequest"
    ) -> "GetBotInfoResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_channel_list(
        self, get_channel_list_request: "GetChannelListRequest"
    ) -> "GetChannelListResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_guild_meta_by_guest(
        self, get_guild_meta_by_guest_request: "GetGuildMetaByGuestRequest"
    ) -> "GetGuildMetaByGuestResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_guild_channel_list(
        self, get_guild_channel_list_request: "GetGuildChannelListRequest"
    ) -> "GetGuildChannelListResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_guild_member_list(
        self, get_guild_member_list_request: "GetGuildMemberListRequest"
    ) -> "GetGuildMemberListResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_guild_member(
        self, get_guild_member_request: "GetGuildMemberRequest"
    ) -> "GetGuildMemberResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def send_channel_message(
        self, send_channel_message_request: "SendChannelMessageRequest"
    ) -> "SendChannelMessageResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_guild_feed_list(
        self, get_guild_feed_list_request: "GetGuildFeedListRequest"
    ) -> "GetGuildFeedListResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_guild_role_list(
        self, get_guild_role_list_request: "GetGuildRoleListRequest"
    ) -> "GetGuildRoleListResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def delete_guild_role(
        self, delete_guild_role_request: "DeleteGuildRoleRequest"
    ) -> "DeleteGuildRoleResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def set_guild_member_role(
        self, set_guild_member_role_request: "SetGuildMemberRoleRequest"
    ) -> "SetGuildMemberRoleResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def update_guild_role(
        self, update_guild_role_request: "UpdateGuildRoleRequest"
    ) -> "UpdateGuildRoleResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def create_guild_role(
        self, create_guild_role_request: "CreateGuildRoleRequest"
    ) -> "CreateGuildRoleResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_get_bot_info(
        self, stream: "grpclib.server.Stream[GetBotInfoRequest, GetBotInfoResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_bot_info(request)
        await stream.send_message(response)

    async def __rpc_get_channel_list(
        self,
        stream: "grpclib.server.Stream[GetChannelListRequest, GetChannelListResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_channel_list(request)
        await stream.send_message(response)

    async def __rpc_get_guild_meta_by_guest(
        self,
        stream: "grpclib.server.Stream[GetGuildMetaByGuestRequest, GetGuildMetaByGuestResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_guild_meta_by_guest(request)
        await stream.send_message(response)

    async def __rpc_get_guild_channel_list(
        self,
        stream: "grpclib.server.Stream[GetGuildChannelListRequest, GetGuildChannelListResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_guild_channel_list(request)
        await stream.send_message(response)

    async def __rpc_get_guild_member_list(
        self,
        stream: "grpclib.server.Stream[GetGuildMemberListRequest, GetGuildMemberListResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_guild_member_list(request)
        await stream.send_message(response)

    async def __rpc_get_guild_member(
        self,
        stream: "grpclib.server.Stream[GetGuildMemberRequest, GetGuildMemberResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_guild_member(request)
        await stream.send_message(response)

    async def __rpc_send_channel_message(
        self,
        stream: "grpclib.server.Stream[SendChannelMessageRequest, SendChannelMessageResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.send_channel_message(request)
        await stream.send_message(response)

    async def __rpc_get_guild_feed_list(
        self,
        stream: "grpclib.server.Stream[GetGuildFeedListRequest, GetGuildFeedListResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_guild_feed_list(request)
        await stream.send_message(response)

    async def __rpc_get_guild_role_list(
        self,
        stream: "grpclib.server.Stream[GetGuildRoleListRequest, GetGuildRoleListResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_guild_role_list(request)
        await stream.send_message(response)

    async def __rpc_delete_guild_role(
        self,
        stream: "grpclib.server.Stream[DeleteGuildRoleRequest, DeleteGuildRoleResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.delete_guild_role(request)
        await stream.send_message(response)

    async def __rpc_set_guild_member_role(
        self,
        stream: "grpclib.server.Stream[SetGuildMemberRoleRequest, SetGuildMemberRoleResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.set_guild_member_role(request)
        await stream.send_message(response)

    async def __rpc_update_guild_role(
        self,
        stream: "grpclib.server.Stream[UpdateGuildRoleRequest, UpdateGuildRoleResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.update_guild_role(request)
        await stream.send_message(response)

    async def __rpc_create_guild_role(
        self,
        stream: "grpclib.server.Stream[CreateGuildRoleRequest, CreateGuildRoleResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.create_guild_role(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/kritor.guild.GuildService/GetBotInfo": grpclib.const.Handler(
                self.__rpc_get_bot_info,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetBotInfoRequest,
                GetBotInfoResponse,
            ),
            "/kritor.guild.GuildService/GetChannelList": grpclib.const.Handler(
                self.__rpc_get_channel_list,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetChannelListRequest,
                GetChannelListResponse,
            ),
            "/kritor.guild.GuildService/GetGuildMetaByGuest": grpclib.const.Handler(
                self.__rpc_get_guild_meta_by_guest,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetGuildMetaByGuestRequest,
                GetGuildMetaByGuestResponse,
            ),
            "/kritor.guild.GuildService/GetGuildChannelList": grpclib.const.Handler(
                self.__rpc_get_guild_channel_list,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetGuildChannelListRequest,
                GetGuildChannelListResponse,
            ),
            "/kritor.guild.GuildService/GetGuildMemberList": grpclib.const.Handler(
                self.__rpc_get_guild_member_list,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetGuildMemberListRequest,
                GetGuildMemberListResponse,
            ),
            "/kritor.guild.GuildService/GetGuildMember": grpclib.const.Handler(
                self.__rpc_get_guild_member,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetGuildMemberRequest,
                GetGuildMemberResponse,
            ),
            "/kritor.guild.GuildService/SendChannelMessage": grpclib.const.Handler(
                self.__rpc_send_channel_message,
                grpclib.const.Cardinality.UNARY_UNARY,
                SendChannelMessageRequest,
                SendChannelMessageResponse,
            ),
            "/kritor.guild.GuildService/GetGuildFeedList": grpclib.const.Handler(
                self.__rpc_get_guild_feed_list,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetGuildFeedListRequest,
                GetGuildFeedListResponse,
            ),
            "/kritor.guild.GuildService/GetGuildRoleList": grpclib.const.Handler(
                self.__rpc_get_guild_role_list,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetGuildRoleListRequest,
                GetGuildRoleListResponse,
            ),
            "/kritor.guild.GuildService/DeleteGuildRole": grpclib.const.Handler(
                self.__rpc_delete_guild_role,
                grpclib.const.Cardinality.UNARY_UNARY,
                DeleteGuildRoleRequest,
                DeleteGuildRoleResponse,
            ),
            "/kritor.guild.GuildService/SetGuildMemberRole": grpclib.const.Handler(
                self.__rpc_set_guild_member_role,
                grpclib.const.Cardinality.UNARY_UNARY,
                SetGuildMemberRoleRequest,
                SetGuildMemberRoleResponse,
            ),
            "/kritor.guild.GuildService/UpdateGuildRole": grpclib.const.Handler(
                self.__rpc_update_guild_role,
                grpclib.const.Cardinality.UNARY_UNARY,
                UpdateGuildRoleRequest,
                UpdateGuildRoleResponse,
            ),
            "/kritor.guild.GuildService/CreateGuildRole": grpclib.const.Handler(
                self.__rpc_create_guild_role,
                grpclib.const.Cardinality.UNARY_UNARY,
                CreateGuildRoleRequest,
                CreateGuildRoleResponse,
            ),
        }
