import re
from io import BytesIO
from pathlib import Path
from typing_extensions import override
from typing import TYPE_CHECKING, Union, Optional

from betterproto import Casing
from grpclib.client import Channel
from nonebot.message import handle_event
from nonebot.compat import type_validate_python

from nonebot.adapters import Bot as BaseBot

from .utils import API, log
from .config import ClientInfo
from .model import Sender, Contact, SceneType
from .message import Reply, Message, MessageSegment
from .event import Event, MessageEvent, MessageEventType
from .protos.kritor.common import Element, ForwardMessageBody
from .protos.kritor.core import (
    CoreServiceStub,
    GetVersionRequest,
    DownloadFileRequest,
    SwitchAccountRequest,
    GetCurrentAccountRequest,
)
from .protos.kritor.process import (
    ProcessServiceStub,
    SetGroupApplyResultRequest,
    SetFriendApplyResultRequest,
    SetInvitedJoinGroupResultRequest,
)
from .protos.kritor.developer import (
    ShellRequest,
    GetLogRequest,
    ClearCacheRequest,
    UploadImageRequest,
    DeveloperServiceStub,
    GetDeviceBatteryRequest,
)
from .protos.kritor.file import (
    DeleteFileRequest,
    UploadFileRequest,
    GetFileListRequest,
    CreateFolderRequest,
    DeleteFolderRequest,
    RenameFolderRequest,
    GroupFileServiceStub,
    GetFileSystemInfoRequest,
)
from .protos.kritor.friend import (
    VoteUserRequest,
    FriendServiceStub,
    GetUidByUinRequest,
    GetUinByUidRequest,
    GetFriendListRequest,
    SetProfileCardRequest,
    IsBlackListUserRequest,
    PrivateChatFileRequest,
    GetFriendProfileCardRequest,
    GetStrangerProfileCardRequest,
    UploadPrivateChatFileResponse,
)
from .protos.kritor.guild import (
    GuildServiceStub,
    GetBotInfoRequest,
    GetChannelListRequest,
    GetGuildMemberRequest,
    CreateGuildRoleRequest,
    DeleteGuildRoleRequest,
    UpdateGuildRoleRequest,
    GetGuildFeedListRequest,
    GetGuildRoleListRequest,
    GetGuildMemberListRequest,
    SendChannelMessageRequest,
    SetGuildMemberRoleRequest,
    GetGuildChannelListRequest,
    GetGuildMetaByGuestRequest,
)
from .protos.kritor.message import (
    GetMessageRequest,
    MessageServiceStub,
    SendMessageRequest,
    SendMessageResponse,
    RecallMessageRequest,
    SetMessageReadRequest,
    GetMessageBySeqRequest,
    GetHistoryMessageRequest,
    SetEssenceMessageRequest,
    SendMessageByResIdRequest,
    DeleteEssenceMessageRequest,
    UploadForwardMessageRequest,
    GetEssenceMessageListRequest,
    ReactMessageWithEmojiRequest,
    DownloadForwardMessageRequest,
    GetHistoryMessageBySeqRequest,
)
from .protos.kritor.group import (
    BanMemberRequest,
    GroupServiceStub,
    KickMemberRequest,
    LeaveGroupRequest,
    PokeMemberRequest,
    GetGroupInfoRequest,
    GetGroupListRequest,
    GetGroupHonorRequest,
    SetGroupAdminRequest,
    ModifyGroupNameRequest,
    UploadGroupFileRequest,
    ModifyMemberCardRequest,
    SetGroupWholeBanRequest,
    UploadGroupFileResponse,
    ModifyGroupRemarkRequest,
    GetGroupMemberInfoRequest,
    GetGroupMemberListRequest,
    GetRemainCountAtAllRequest,
    SetGroupUniqueTitleRequest,
    GetNotJoinedGroupInfoRequest,
    GetProhibitedUserListRequest,
)

if TYPE_CHECKING:
    from .adapter import Adapter


async def _check_reply(
    bot: "Bot",
    event: MessageEvent,
) -> None:
    """检查消息中存在的回复，赋值 `event.reply`, `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    message = event.get_message()
    try:
        index = message.index("reply")
    except ValueError:
        return

    msg_seg = message[index]
    if TYPE_CHECKING:
        assert isinstance(msg_seg, Reply)
    del message[index]
    event.reply = msg_seg  # type: ignore
    try:
        origin = (await bot.get_message(message_id=msg_seg.data["message_id"])).message
    except Exception:
        return
    replied_message: MessageEvent = type_validate_python(MessageEventType, origin.to_pydict(casing=Casing.SNAKE))  # type: ignore
    event._replied_message = replied_message
    event.to_me = replied_message.get_user_id() == bot.info.account
    if (
        len(message) > index
        and message[index].type == "at"
        and (message[index].get("uid") == bot.info.account or message[index].data["uid"] == bot.info.account)
    ):
        del message[index]
    if len(message) > index and message[index].type == "text":
        message[index].data["text"] = message[index].data["text"].lstrip()
        if not message[index].data["text"]:
            del message[index]
    if not message:
        message.append(MessageSegment.text(""))


def _check_at_me(
    bot: "Bot",
    event: MessageEvent,
):
    def _is_at_me_seg(segment: MessageSegment) -> bool:
        return segment.type == "at" and (
            segment.get("uid") == bot.info.account or segment.data["uid"] == bot.info.account
        )

    message = event.get_message()

    # ensure message is not empty
    if not message:
        message.append(MessageSegment.text(""))

    deleted = False
    if _is_at_me_seg(message[0]):
        message.pop(0)
        event.to_me = True
        deleted = True
        if message and message[0].type == "text":
            message[0].data["text"] = message[0].data["text"].lstrip("\xa0").lstrip()
            if not message[0].data["text"]:
                del message[0]

    if not deleted:
        # check the last segment
        i = -1
        last_msg_seg = message[i]
        if last_msg_seg.type == "text" and not last_msg_seg.data["text"].strip() and len(message) >= 2:
            i -= 1
            last_msg_seg = message[i]

        if _is_at_me_seg(last_msg_seg):
            event.to_me = True
            del message[i:]

    if not message:
        message.append(MessageSegment.text(""))


def _check_nickname(bot: "Bot", event: MessageEvent) -> None:
    """检查消息开头是否存在昵称，去除并赋值 `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    message = event.get_message()
    first_msg_seg = message[0]
    if first_msg_seg.type != "text":
        return

    nicknames = {re.escape(n) for n in bot.config.nickname}
    if not nicknames:
        return

    # check if the user is calling me with my nickname
    nickname_regex = "|".join(nicknames)
    first_text = first_msg_seg.data["text"]
    if m := re.search(rf"^({nickname_regex})([\s,，]*|$)", first_text, re.IGNORECASE):
        log("DEBUG", f"User is calling me {m[1]}")
        event.to_me = True
        first_msg_seg.data["text"] = first_text[m.end() :]


class Bot(BaseBot):
    adapter: "Adapter"

    @override
    def __init__(self, adapter: "Adapter", self_id: str, info: ClientInfo, client: Channel, need_auth: bool = True):
        super().__init__(adapter, self_id)

        # Bot 配置信息
        self.info: ClientInfo = info
        self.client: Channel = client

        if need_auth:
            metadata = {"ticket": info.ticket}
        else:
            metadata = {}

        class service:
            core = CoreServiceStub(client, metadata=metadata)
            developer = DeveloperServiceStub(client, metadata=metadata)
            group = GroupServiceStub(client, metadata=metadata)
            friend = FriendServiceStub(client, metadata=metadata)
            guild = GuildServiceStub(client, metadata=metadata)
            file = GroupFileServiceStub(client, metadata=metadata)
            message = MessageServiceStub(client, metadata=metadata)
            process = ProcessServiceStub(client, metadata=metadata)

        self.service = service

    def __getattr__(self, item):
        raise AttributeError(f"'Bot' object has no attribute '{item}'")

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, MessageEvent):
            await _check_reply(self, event)
            _check_at_me(self, event)
            _check_nickname(self, event)
        await handle_event(self, event)

    @API
    async def get_version(self):
        """获取协议端的 Kritor 版本信息"""
        return await self.service.core.get_version(GetVersionRequest())

    @API
    async def clear_cache(self):
        """清除缓存"""
        return await self.service.developer.clear_cache(ClearCacheRequest())

    @API
    async def download_file(
        self,
        *,
        url: Optional[str] = None,
        base64: Optional[str] = None,
        root_path: Optional[str] = None,
        file_name: Optional[str] = None,
        thread_cnt: Optional[int] = None,
        headers: Optional[Union[str, dict[str, str]]] = None,
    ):
        """请求Kritor端下载文件

        参数:
            url: 下载文件的URL 二选一
            base64: 下载文件的base64 二选一
            root_path: 下载文件的根目录 需要保证Kritor有该目录访问权限，否则会报错 可选
            file_name: 保存的文件名称 默认为文件MD5 可选
            thread_cnt: 下载文件的线程数 默认为3 可选
            headers: 下载文件的请求头 可选
        """
        if isinstance(headers, dict):
            _headers = "[\r\n]".join([f"{k}={v}" for k, v in headers.items()])
        else:
            _headers = headers
        return await self.service.core.download_file(
            DownloadFileRequest(
                url=url,
                base64=base64,
                root_path=root_path,
                file_name=file_name,
                thread_cnt=thread_cnt,
                headers=_headers,
            )
        )

    @API
    async def get_current_account(self):
        """获取当前账号信息"""
        return await self.service.core.get_current_account(GetCurrentAccountRequest())

    @API
    async def switch_account(
        self,
        *,
        account: Union[str, int],
        super_ticket: str,
    ) -> None:
        """切换账号

        参数:
            account: 账号
            super_ticket: 超级票据
        """
        args = (
            {"account_uin": account, "super_ticket": super_ticket}
            if isinstance(account, int)
            else {"account_uid": account, "super_ticket": super_ticket}
        )
        await self.service.core.switch_account(SwitchAccountRequest().from_pydict(args))

    @API
    async def get_device_battery(self):
        """获取设备电量"""
        return await self.service.developer.get_device_battery(GetDeviceBatteryRequest())

    @API
    async def shell(
        self,
        *,
        command: list[str],
        directory: str,
    ):
        """让协议端执行shell命令

        参数:
            command: shell命令
            directory: 执行目录
        """
        return await self.service.developer.shell(ShellRequest(command=command, directory=directory))

    @API
    async def get_log(
        self,
        *,
        start: int,
        recent: bool = True,
    ):
        """获取日志

        参数:
            start: 起始位置
            recent: 是否获取最新日志
        """
        return await self.service.developer.get_log(GetLogRequest(start=start, recent=recent))

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> SendMessageResponse:
        if not isinstance(event, MessageEvent):
            raise RuntimeError("Event cannot be replied to!")
        if event.contact.type == SceneType.GUILD:
            resp = await self.send_channel_message(
                guild_id=int(event.contact.id),
                channel_id=int(event.contact.sub_id or "0"),
                message=str(message),
                **kwargs,
            )
            return SendMessageResponse(message_id=resp.message_id, message_time=resp.message_time)
        if isinstance(message, str):
            message = Message(message)
        elif isinstance(message, MessageSegment):
            message = Message([message])
        elements = message.to_elements()
        return await self.send_message(contact=event.contact, elements=elements, message_id=event.message_id)

    @API
    async def send_message(
        self,
        *,
        contact: Contact,
        elements: list[Element],
        message_id: Optional[str] = None,
    ) -> SendMessageResponse:
        """发送消息

        参数:
            contact: 要发送的目标
            message: 要发送的消息
            message_id: 可能的回复的消息ID，用于被动消息
        """
        if contact.type == SceneType.GUILD:
            raise ValueError("Guild contact is not supported in this method. Use send_channel_message instead.")
        return await self.service.message.send_message(
            SendMessageRequest(contact=contact.dump(), elements=elements, message_id=message_id)
        )

    @API
    async def send_message_by_res_id(
        self,
        *,
        res_id: str,
        contact: Contact,
    ):
        """通过资源ID发送消息（发送转发消息）

        参数:
            res_id: 资源ID
            contact: 要发送的目标
        """

        return await self.service.message.send_message_by_res_id(
            SendMessageByResIdRequest(res_id=res_id, contact=contact.dump())
        )

    @API
    async def get_message(
        self,
        *,
        message_id: str,
    ):
        """获取消息

        参数:
            message_id: 消息ID
        """

        return await self.service.message.get_message(GetMessageRequest(message_id=message_id))

    @API
    async def get_message_by_seq(
        self,
        *,
        message_seq: int,
    ):
        """获取消息

        参数:
            message_seq: 消息序号
        """

        return await self.service.message.get_message_by_seq(GetMessageBySeqRequest(message_seq=message_seq))

    @API
    async def get_history_message(
        self,
        *,
        contact: Contact,
        start_message_id: Optional[str] = None,
        count: int = 10,
    ):
        """获取历史消息

        参数:
            contact: 要获取的目标
            start_message_id: 起始消息ID, 为空则从最新消息开始
            count: 获取数量
        """

        return await self.service.message.get_history_message(
            GetHistoryMessageRequest(contact=contact.dump(), start_message_id=start_message_id, count=count)
        )

    @API
    async def recall_message(
        self,
        *,
        message_id: str,
    ):
        """撤回消息

        参数:
            message_id: 消息ID
        """

        return await self.service.message.recall_message(RecallMessageRequest(message_id=message_id))

    @API
    async def set_message_comment_emoji(
        self,
        *,
        contact: Contact,
        message_id: str,
        emoji: int,
        is_set: bool = True,
    ):
        """给消息评论表情

        参数:
            contact: 要发送的目标
            message_id: 消息ID
            emoji: 表情
            is_set: 是否评论, False为撤销评论
        """

        return await self.service.message.react_message_with_emoji(
            ReactMessageWithEmojiRequest(contact=contact.dump(), message_id=message_id, face_id=emoji, is_set=is_set)
        )

    @API
    async def delete_essence_message(
        self,
        *,
        group_id: Union[int, str, Contact],
        message_id: str,
    ):
        """删除精华消息

        参数:
            group_id: 群ID
            message_id: 消息ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.message.delete_essence_message(
            DeleteEssenceMessageRequest(group_id=_group_id, message_id=message_id)
        )

    @API
    async def get_essence_message_list(
        self,
        *,
        group_id: Union[int, str, Contact],
    ):
        """获取精华消息列表

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return (
            await self.service.message.get_essence_message_list(GetEssenceMessageListRequest(group_id=_group_id))
        ).messages

    @API
    async def set_essence_message(
        self,
        *,
        group_id: Union[int, str, Contact],
        message_id: str,
    ):
        """设置精华消息

        参数:
            group_id: 群ID
            message_id: 消息ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.message.set_essence_message(
            SetEssenceMessageRequest(group_id=_group_id, message_id=message_id)
        )

    @API
    async def get_forward_message(
        self,
        *,
        res_id: str,
    ):
        """获取转发消息

        参数:
            res_d: 合并转发元素内的资源ID
        """

        return await self.service.message.download_forward_message(DownloadForwardMessageRequest(res_id=res_id))

    @API
    async def upload_forward_message(
        self,
        *,
        contact: Contact,
        messages: list[ForwardMessageBody],
    ):
        """上传合并转发消息

        参数:
            contact: 要发送的目标
            messages: 要发送的合并转发消息
        """

        return await self.service.message.upload_forward_message(
            UploadForwardMessageRequest(contact=contact.dump(), messages=messages)
        )

    async def send_forward_message(
        self,
        contact: Contact,
        messages: list[ForwardMessageBody],
    ):
        """发送合并转发消息，即上传合并转发消息并通过返回的资源ID发送

        参数:
            contact: 要发送的目标
            messages: 要发送的合并转发消息
        """

        resp = await self.service.message.upload_forward_message(
            UploadForwardMessageRequest(contact=contact.dump(), messages=messages)
        )
        return await self.service.message.send_message_by_res_id(
            SendMessageByResIdRequest(res_id=resp.res_id, contact=contact.dump())
        )

    @API
    async def set_message_readed(
        self,
        *,
        contact: Contact,
    ):
        """设置消息已读

        参数:
            contact: 要发送的目标
        """

        return await self.service.message.set_message_readed(SetMessageReadRequest(contact=contact.dump()))

    @API
    async def get_history_message_by_seq(
        self,
        *,
        contact: Contact,
        start_message_seq: int,
        count: int = 10,
    ):
        """获取历史消息

        参数:
            contact: 要获取的目标
            start_message_seq: 起始消息序号, 为空则从最新消息开始
            count: 获取数量
        """

        return await self.service.message.get_history_message_by_seq(
            GetHistoryMessageBySeqRequest(contact=contact.dump(), start_message_seq=start_message_seq, count=count)
        )

    @API
    async def upload_private_file(
        self,
        *,
        user_id: Union[int, str, Contact],
        path: Union[str, Path],
        name: Optional[str] = None,
    ) -> UploadPrivateChatFileResponse:
        """上传私聊文件

        参数:
            user_id: 用户ID
            path: 文件路径
            name: 文件名
        """
        if isinstance(user_id, Contact):
            if user_id.type != SceneType.FRIEND:
                raise ValueError("Contact must be FRIEND")
            _user_id = user_id.id
        else:
            _user_id = str(user_id)
        file = Path(path).resolve().absolute()
        if not name:
            name = file.name
        return await self.service.friend.upload_private_file(
            PrivateChatFileRequest(user_id=_user_id, file=file.as_posix(), name=name)
        )

    @API
    async def upload_group_file(
        self,
        *,
        group_id: Union[int, str, Contact],
        path: Union[str, Path],
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> UploadGroupFileResponse:
        """上传群文件

        参数:
            group_id: 群ID
            path: 文件路径
            name: 文件名
            folder_id: 文件夹ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        file = Path(path).resolve().absolute()
        if not name:
            name = file.name
        return await self.service.group.upload_group_file(
            UploadGroupFileRequest(group_id=_group_id, file=file.as_posix(), name=name, folder=folder_id)
        )

    @API
    async def create_folder(
        self,
        *,
        group_id: Union[int, str, Contact],
        name: str,
    ):
        """创建文件夹

        参数:
            group_id: 群ID
            name: 文件夹名
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.file.create_folder(CreateFolderRequest(group_id=_group_id, name=name))

    @API
    async def delete_folder(
        self,
        *,
        group_id: Union[int, str, Contact],
        folder_id: str,
    ):
        """删除文件夹

        参数:
            group_id: 群ID
            folder_id: 文件夹ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.file.delete_folder(DeleteFolderRequest(group_id=_group_id, folder_id=folder_id))

    @API
    async def upload_file(
        self,
        *,
        group_id: Union[int, str, Contact],
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        raw: Optional[Union[bytes, BytesIO]] = None,
    ):
        """上传文件

        参数:
            group_id: 群ID
            url: 图片链接
            path: 图片路径
            raw: 图片二进制数据
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if url:
            args = {"file_url": url, "group_id": _group_id}
        elif path:
            file = Path(path).resolve().absolute()
            args = {"file_path": str(file), "file_name": file.name, "group_id": _group_id}
        elif raw:
            args = {"file": raw if isinstance(raw, bytes) else raw.getvalue(), "group_id": _group_id}
        else:
            raise ValueError("No file provided")
        return await self.service.file.upload_file(UploadFileRequest().from_pydict(args))

    @API
    async def delete_file(
        self,
        *,
        group_id: Union[int, str, Contact],
        file_id: str,
        bus_id: int,
    ):
        """删除文件

        参数:
            group_id: 群ID
            file_id: 文件ID
            bus_id: 文件类型ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.file.delete_file(
            DeleteFileRequest(group_id=_group_id, file_id=file_id, bus_id=bus_id)
        )

    @API
    async def rename_folder(
        self,
        *,
        group_id: Union[int, str, Contact],
        folder_id: str,
        name: str,
    ):
        """重命名文件夹

        参数:
            group_id: 群ID
            folder_id: 文件夹ID
            name: 文件夹名
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.file.rename_folder(
            RenameFolderRequest(group_id=_group_id, folder_id=folder_id, name=name)
        )

    @API
    async def get_file_system_info(
        self,
        *,
        group_id: Union[int, str, Contact],
    ):
        """获取文件系统信息

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.file.get_file_system_info(GetFileSystemInfoRequest(group_id=_group_id))

    @API
    async def get_file_list(
        self,
        *,
        group_id: Union[int, str, Contact],
        folder_id: Optional[str] = None,
    ):
        """获取文件列表

        参数:
            group_id: 群ID
            folder_id: 文件夹ID, 为空则获取根目录
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.file.get_file_list(GetFileListRequest(group_id=_group_id, folder_id=folder_id))

    async def get_file(
        self,
        group_id: Union[int, str, Contact],
        file_id: str,
        folder_id: Optional[str] = None,
    ):
        """获取文件, 即先获取文件列表再下载文件

        参数:
            group_id: 群ID
            file_id: 文件ID
            folder_id: 文件夹ID, 为空则获取根目录
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        files = await self.service.file.get_file_list(GetFileListRequest(group_id=_group_id, folder_id=folder_id))
        for file in files.files:
            if file.file_id == file_id:
                return file
        raise ValueError(f"File {file_id} not found")

    @API
    async def get_bot_info(
        self,
    ):
        """获取频道系统内的Bot信息"""

        return await self.service.guild.get_bot_info(GetBotInfoRequest())

    @API
    async def get_guild_list(
        self,
    ):
        """获取频道列表"""

        return (await self.service.guild.get_channel_list(GetChannelListRequest())).get_guild_list

    @API
    async def get_guild_channel_list(
        self,
        *,
        guild_id: Union[int, str, Contact],
        refresh: bool = False,
    ):
        """获取频道内的频道列表

        参数:
            guild_id: 频道ID
            refresh: 是否刷新
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return (
            await self.service.guild.get_guild_channel_list(
                GetGuildChannelListRequest(guild_id=_guild_id, refresh=refresh)
            )
        ).channels_info

    @API
    async def get_guild_meta_by_guest(
        self,
        *,
        guild_id: Union[int, str, Contact],
    ):
        """获取频道信息

        参数:
            guild_id: 频道ID
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.get_guild_meta_by_guest(GetGuildMetaByGuestRequest(guild_id=_guild_id))

    @API
    async def get_guild_member_list(
        self,
        *,
        guild_id: Union[int, str, Contact],
        next_token: Optional[str] = None,
        all: bool = False,
        refresh: bool = False,
    ):
        """获取频道成员列表

        参数:
            guild_id: 频道ID
            next_token: 下一页标识
            all: 是否一次性获取全部
            refresh: 是否刷新
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.get_guild_member_list(
            GetGuildMemberListRequest(guild_id=_guild_id, next_token=next_token or "", all=all, refresh=refresh)
        )

    @API
    async def get_guild_member(
        self,
        *,
        guild_id: Union[int, str, Contact],
        tiny_id: int,
    ):
        """获取频道成员

        参数:
            guild_id: 频道ID
            tiny_id: 成员tinyId
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.get_guild_member(GetGuildMemberRequest(guild_id=_guild_id, tiny_id=tiny_id))

    @API
    async def send_channel_message(
        self,
        *,
        guild_id: int,
        channel_id: int,
        message: str,
        recall_duration: int = 0,
    ):
        """发送频道消息

        参数:
            guild_id: 频道ID
            channel_id: 子频道ID
            message: 消息体
            recall_duration: 自动撤回间隔
        """
        return await self.service.guild.send_channel_message(
            SendChannelMessageRequest(
                guild_id=guild_id, channel_id=channel_id, message=message, recall_duration=recall_duration
            )
        )

    @API
    async def get_guild_feed_list(
        self,
        *,
        guild_id: Union[int, str, Contact],
        from_: int,
    ):
        """获取频道帖子广场列表

        参数:
            guild_id: 频道ID
            from_: 起始位置
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.get_guild_feed_list(GetGuildFeedListRequest(guild_id=_guild_id, from_=from_))

    @API
    async def get_guild_role_list(
        self,
        *,
        guild_id: Union[int, str, Contact],
    ):
        """获取频道身份组列表

        参数:
            guild_id: 频道ID
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return (await self.service.guild.get_guild_role_list(GetGuildRoleListRequest(guild_id=_guild_id))).roles_info

    @API
    async def create_guild_role(
        self,
        *,
        guild_id: Union[int, str, Contact],
        name: str,
        color: int,
    ):
        """创建频道身份组

        参数:
            guild_id: 频道ID
            name: 身份组名
            color: 颜色ARGB
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.create_guild_role(
            CreateGuildRoleRequest(guild_id=_guild_id, name=name, color=color)
        )

    @API
    async def update_guild_role(
        self,
        *,
        guild_id: Union[int, str, Contact],
        role_id: int,
        name: str,
        color: int,
    ):
        """更新频道身份组

        参数:
            guild_id: 频道ID
            role_id: 身份组ID
            name: 身份组名
            color: 颜色ARGB
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.update_guild_role(
            UpdateGuildRoleRequest(guild_id=_guild_id, role_id=role_id, name=name, color=color)
        )

    @API
    async def delete_guild_role(
        self,
        *,
        guild_id: Union[int, str, Contact],
        role_id: int,
    ):
        """删除频道身份组

        参数:
            guild_id: 频道ID
            role_id: 身份组ID
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.delete_guild_role(DeleteGuildRoleRequest(guild_id=_guild_id, role_id=role_id))

    @API
    async def set_guild_member_role(
        self,
        *,
        guild_id: Union[int, str, Contact],
        role_id: int,
        is_set: bool,
        users: list[str],
    ):
        """设置频道成员身份

        参数:
            guild_id: 频道ID
            role_id: 身份组ID
            is_set: 是否设置
            users: 用户tinyId列表
        """
        if isinstance(guild_id, Contact):
            if guild_id.type != SceneType.GUILD:
                raise ValueError("Contact must be GUILD")
            _guild_id = int(guild_id.id)
        else:
            _guild_id = int(guild_id)
        return await self.service.guild.set_guild_member_role(
            SetGuildMemberRoleRequest(guild_id=_guild_id, role_id=role_id, set=is_set, tiny_ids=users)
        )

    @API
    async def upload_image(
        self,
        *,
        group_id: Union[int, str, Contact],
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        raw: Optional[Union[bytes, BytesIO]] = None,
    ):
        """上传图片

        参数:
            group_id: 群ID
            url: 图片链接
            path: 图片路径
            raw: 图片二进制数据
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if url:
            args = {"file_url": url, "group_id": _group_id}
        elif path:
            file = Path(path).resolve().absolute()
            args = {"file_path": str(file), "file_name": file.name, "group_id": _group_id}
        elif raw:
            args = {"file": raw if isinstance(raw, bytes) else raw.getvalue(), "group_id": _group_id}
        else:
            raise ValueError("No file provided")
        return await self.service.developer.upload_image(UploadImageRequest().from_pydict(args))

    @API
    async def get_uid_by_uin(
        self,
        *,
        target_uins: list[int],
    ):
        """获取UID

        参数:
            target_uins: UIN列表
        """
        return (await self.service.friend.get_uid_by_uin(GetUidByUinRequest(target_uins=target_uins))).uid_map

    @API
    async def get_uin_by_uid(
        self,
        *,
        target_uids: list[str],
    ):
        """获取UIN

        参数:
            target_uids: UID列表
        """
        return (await self.service.friend.get_uin_by_uid(GetUinByUidRequest(target_uids=target_uids))).uin_map

    @API
    async def get_friend_list(
        self,
        refresh: bool = False,
    ):
        """获取好友列表

        参数:
            refresh: 是否刷新
        """
        return (await self.service.friend.get_friend_list(GetFriendListRequest(refresh=refresh))).friends_info

    @API
    async def get_friend_profile_card(self, *, targets: Union[list[Union[str, int]], Contact, Sender]):
        """获取好友名片

        参数:
            targets: UIN列表 或 UID列表
        """
        target_uins = []
        target_uids = []
        if isinstance(targets, Contact):
            if targets.type != SceneType.FRIEND:
                raise ValueError("Contact must be FRIEND")
            target_uins.append(int(targets.id))
        elif isinstance(targets, Sender):
            target_uins.append(targets.uin) if targets.uin else target_uids.append(targets.uid)
        else:
            target_uins.extend(i for i in targets if isinstance(i, int))
            target_uids.extend(i for i in targets if isinstance(i, str))
        return await self.service.friend.get_friend_profile_card(
            GetFriendProfileCardRequest(target_uids=target_uids, target_uins=target_uins)
        )

    @API
    async def get_stranger_profile_card(self, *, targets: Union[list[Union[str, int]], Contact, Sender]):
        """获取陌生人名片

        参数:
            targets: UIN列表 或 UID列表
        """
        target_uins = []
        target_uids = []
        if isinstance(targets, Contact):
            if targets.type != SceneType.FRIEND:
                raise ValueError("Contact must be FRIEND")
            target_uins.append(int(targets.id))
        elif isinstance(targets, Sender):
            target_uins.append(targets.uin) if targets.uin else target_uids.append(targets.uid)
        else:
            target_uins.extend(i for i in targets if isinstance(i, int))
            target_uids.extend(i for i in targets if isinstance(i, str))
        return await self.service.friend.get_stranger_profile_card(
            GetStrangerProfileCardRequest(target_uids=target_uids, target_uins=target_uins)
        )

    @API
    async def is_black_list_user(
        self,
        *,
        target: Union[str, int, Contact, Sender],
    ):
        """是否黑名单用户

        参数:
            target: UIN 或 UID
        """
        if isinstance(target, Contact):
            if target.type not in (
                SceneType.FRIEND,
                SceneType.STRANGER,
                SceneType.STRANGER_FROM_GROUP,
                SceneType.NEARBY,
            ):
                raise ValueError("Contact must be FRIEND")
            target_uin = int(target.id)
            args = {"target_uin": target_uin}
        elif isinstance(target, Sender):
            args = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        return await self.service.friend.is_black_list_user(IsBlackListUserRequest().from_pydict(args))

    @API
    async def set_profile_card(
        self,
        *,
        nick_name: Optional[str] = None,
        company: Optional[str] = None,
        email: Optional[str] = None,
        college: Optional[str] = None,
        personal_note: Optional[str] = None,
        birthday: Optional[int] = None,
        age: Optional[int] = None,
    ):
        """设置个人名片

        参数:
            nick_name: 昵称
            company: 公司
            email: 邮箱
            college: 学校
            personal_note: 个性签名
            birthday: 生日
            age: 年龄
        """
        await self.service.friend.set_profile_card(
            SetProfileCardRequest(
                nick_name=nick_name,
                company=company,
                email=email,
                college=college,
                personal_note=personal_note,
                birthday=birthday,
                age=age,
            )
        )

    @API
    async def vote_user(
        self,
        *,
        target: Union[str, int, Contact, Sender],
        vote_count: int = 1,
    ):
        """点赞用户

        参数:
            target: UIN 或 UID
            vote_count: 点赞数量
        """
        if isinstance(target, Contact):
            if target.type not in (
                SceneType.FRIEND,
                SceneType.STRANGER,
                SceneType.STRANGER_FROM_GROUP,
                SceneType.NEARBY,
            ):
                raise ValueError("Contact must be FRIEND")
            args = {"target_uin": int(target.id), "vote_count": vote_count}
        elif isinstance(target, Sender):
            args = (
                {"target_uin": target.uin, "vote_count": vote_count}
                if target.uin
                else {"target_uid": target.uid, "vote_count": vote_count}
            )
        else:
            args = (
                {"target_uin": target, "vote_count": vote_count}
                if isinstance(target, int)
                else {"target_uid": target, "vote_count": vote_count}
            )
        return await self.service.friend.vote_user(VoteUserRequest().from_pydict(args))

    @API
    async def get_group_info(
        self,
        *,
        group_id: Union[int, str, Contact],
    ):
        """获取群信息

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return (await self.service.group.get_group_info(GetGroupInfoRequest(group_id=_group_id))).group_info

    @API
    async def get_group_list(
        self,
    ):
        """获取群列表"""

        return (await self.service.group.get_group_list(GetGroupListRequest())).groups_info

    @API
    async def get_group_member_info(
        self,
        *,
        group_id: Union[int, str, Contact],
        target: Union[int, str, Sender],
        refresh: bool = False,
    ):
        """获取群成员信息

        参数:
            group_id: 群ID
            target: UIN 或 UID
            refresh: 是否刷新
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if isinstance(target, Sender):
            args: dict = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args: dict = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        args["group_id"] = _group_id
        args["refresh"] = refresh
        return (
            await self.service.group.get_group_member_info(GetGroupMemberInfoRequest().from_pydict(args))
        ).group_member_info

    @API
    async def get_group_member_list(
        self,
        *,
        group_id: Union[int, str, Contact],
        refresh: bool = False,
    ):
        """获取群成员列表

        参数:
            group_id: 群ID
            refresh: 是否刷新
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return (
            await self.service.group.get_group_member_list(
                GetGroupMemberListRequest(group_id=_group_id, refresh=refresh)
            )
        ).group_members_info

    @API
    async def get_group_prohibited_user_list(
        self,
        *,
        group_id: Union[int, str, Contact],
    ):
        """获取群被禁言用户列表

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return (
            await self.service.group.get_prohibited_user_list(GetProhibitedUserListRequest(group_id=_group_id))
        ).prohibited_users_info

    @API
    async def ban_member(
        self,
        *,
        group_id: Union[int, str, Contact],
        target: Union[int, str, Sender],
        duration: int = 0,
    ) -> None:
        """禁言成员

        参数:
            group_id: 群ID
            target: UIN 或 UID
            duration: 禁言时长, 0为解除禁言
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if isinstance(target, Sender):
            args: dict = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args: dict = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        await self.service.group.ban_member(BanMemberRequest(group_id=_group_id, **args, duration=duration))

    @API
    async def nudge_member(
        self,
        *,
        group_id: Union[int, str, Contact],
        target: Union[int, str, Sender],
    ) -> None:
        """双击成员头像

        参数:
            group_id: 群ID
            target: UIN 或 UID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if isinstance(target, Sender):
            args: dict = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args: dict = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        await self.service.group.poke_member(PokeMemberRequest(group_id=_group_id, **args))

    @API
    async def kick_member(
        self,
        *,
        group_id: Union[int, str, Contact],
        target: Union[int, str, Sender],
        reject_add_request: bool = False,
        reason: Optional[str] = None,
    ) -> None:
        """踢出成员

        参数:
            group_id: 群ID
            targets: UIN 或 UID
            reject_add_request: 是否拒绝再次加群
            reason: 踢出原因
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if isinstance(target, Sender):
            args: dict = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args: dict = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        await self.service.group.kick_member(
            KickMemberRequest(group_id=_group_id, **args, reject_add_request=reject_add_request, kick_reason=reason)
        )

    @API
    async def leave_group(
        self,
        *,
        group_id: Union[int, str, Contact],
    ) -> None:
        """机器人主动退群

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        await self.service.group.leave_group(LeaveGroupRequest(group_id=_group_id))

    @API
    async def modify_member_card(
        self,
        *,
        group_id: Union[int, str, Contact],
        target: Union[int, str, Sender],
        card: str,
    ) -> None:
        """修改群名片

        参数:
            group_id: 群ID
            target: UIN列表 或 UID列表
            card: 新的群名片
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if isinstance(target, Sender):
            args: dict = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args: dict = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        await self.service.group.modify_member_card(ModifyMemberCardRequest(group_id=_group_id, **args, card=card))

    @API
    async def modify_group_name(
        self,
        *,
        group_id: Union[int, str, Contact],
        name: str,
    ) -> None:
        """修改群名称

        参数:
            group_id: 群ID
            name: 新的群名称
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        await self.service.group.modify_group_name(ModifyGroupNameRequest(group_id=_group_id, group_name=name))

    @API
    async def modify_group_remark(
        self,
        *,
        group_id: Union[int, str, Contact],
        remark: str,
    ) -> None:
        """修改群备注

        参数:
            group_id: 群ID
            remark: 新的群备注
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        await self.service.group.modify_group_remark(ModifyGroupRemarkRequest(group_id=_group_id, remark=remark))

    @API
    async def set_group_admin(
        self,
        *,
        group_id: Union[int, str, Contact],
        target: Union[int, str, Sender],
        is_set: bool,
    ) -> None:
        """设置管理员

        参数:
            group_id: 群ID
            target: UIN 或 UID
            is_set: 是否设置为管理员
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if isinstance(target, Sender):
            args: dict = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args: dict = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        await self.service.group.set_group_admin(SetGroupAdminRequest(group_id=_group_id, **args, is_admin=is_set))

    @API
    async def set_group_unique_title(
        self,
        *,
        group_id: Union[int, str, Contact],
        target: Union[int, str, Sender],
        title: str,
    ) -> None:
        """设置专属头衔

        参数:
            group_id: 群ID
            target: UIN 或 UID
            title: 新的群头衔
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        if isinstance(target, Sender):
            args: dict = {"target_uin": target.uin} if target.uin else {"target_uid": target.uid}
        else:
            args: dict = {"target_uin": target} if isinstance(target, int) else {"target_uid": target}
        await self.service.group.set_group_unique_title(
            SetGroupUniqueTitleRequest(group_id=_group_id, **args, unique_title=title)
        )

    @API
    async def set_group_whole_ban(
        self,
        *,
        group_id: Union[int, str, Contact],
        is_ban: bool,
    ) -> None:
        """全员禁言

        参数:
            group_id: 群ID
            is_ban: 是否全员禁言
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        await self.service.group.set_group_whole_ban(SetGroupWholeBanRequest(group_id=_group_id, is_ban=is_ban))

    @API
    async def get_remain_count_at_all(
        self,
        *,
        group_id: Union[int, str, Contact],
    ):
        """获取剩余全体@次数

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return await self.service.group.get_remain_count_at_all(GetRemainCountAtAllRequest(group_id=_group_id))

    @API
    async def get_not_joined_group_info(
        self,
        *,
        group_id: Union[int, str, Contact],
    ):
        """获取未加入群信息

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return (
            await self.service.group.get_not_joined_group_info(GetNotJoinedGroupInfoRequest(group_id=_group_id))
        ).group_info

    @API
    async def get_group_honor(
        self,
        *,
        group_id: Union[int, str, Contact],
        refresh: bool = False,
    ):
        """获取群荣誉信息

        参数:
            group_id: 群ID
        """
        if isinstance(group_id, Contact):
            if group_id.type != SceneType.GROUP:
                raise ValueError("Contact must be GROUP")
            _group_id = int(group_id.id)
        else:
            _group_id = int(group_id)
        return (
            await self.service.group.get_group_honor(GetGroupHonorRequest(group_id=_group_id, refresh=refresh))
        ).group_honors_info

    @API
    async def reply_new_friend_request(
        self,
        *,
        request_id: str,
        is_approve: bool,
        reason: Optional[str] = None,
    ):
        """回复好友请求

        参数:
            request_id: 请求ID
            is_approve: 是否同意
            reason: 拒绝理由
        """
        await self.service.process.set_friend_apply_result(
            SetFriendApplyResultRequest(request_id=request_id, is_approve=is_approve, remark=reason)
        )

    @API
    async def reply_add_member_request(
        self,
        *,
        request_id: str,
        is_approve: bool,
        reason: Optional[str] = None,
    ):
        """回复新群友加群请求

        参数:
            request_id: 请求ID
            is_approve: 是否同意
            reason: 拒绝理由
        """
        await self.service.process.set_group_apply_result(
            SetGroupApplyResultRequest(request_id=request_id, is_approve=is_approve, deny_reason=reason)
        )

    @API
    async def reply_invite_group_request(
        self,
        *,
        request_id: str,
        is_approve: bool,
    ):
        """回复邀请入群请求

        参数:
            request_id: 请求ID
            is_approve: 是否同意
        """
        await self.service.process.set_invited_join_group_result(
            SetInvitedJoinGroupResultRequest(request_id=request_id, is_approve=is_approve)
        )
