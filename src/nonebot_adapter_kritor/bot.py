import re
import json
from typing_extensions import override
from typing import TYPE_CHECKING, Any, Dict, List, Union, Optional

from nonebot.message import handle_event
from nonebot.drivers import Request, Response
from nonebot.compat import type_validate_python

from nonebot.adapters import Bot as BaseBot

from .utils import API, log
from .config import ClientInfo
from .event import Event, MessageEvent, MessageEventType
from .message import Message, MessageSegment, Reply
from .model import Contact

from grpclib.client import Channel
from betterproto import Casing

from .protos.kritor.common import Element
from .protos.kritor.message import (
    MessageServiceStub, 
    SendMessageRequest, 
    SendMessageResponse,
    SendMessageByResIdRequest,
    GetMessageRequest,
    RecallMessageRequest,
    ReactMessageWithEmojiRequest,
    SetMessageReadRequest,
    GetMessageBySeqRequest,
    GetHistoryMessageRequest,
    SetEssenceMessageRequest,
    DeleteEssenceMessageRequest,
    UploadForwardMessageRequest,
    GetEssenceMessageListRequest,
    DownloadForwardMessageRequest,
    GetHistoryMessageBySeqRequest,
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
        return segment.type == "at" and (segment.get("uid") == bot.info.account or segment.data["uid"] == bot.info.account)

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
    def __init__(self, adapter: "Adapter", self_id: str, info: ClientInfo, client: Channel):
        super().__init__(adapter, self_id)

        # Bot 配置信息
        self.info: ClientInfo = info
        self.client: Channel = client

    def __getattr__(self, item):
        raise AttributeError(f"'Bot' object has no attribute '{item}'")

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, MessageEvent):
            await _check_reply(self, event)
            _check_at_me(self, event)
            _check_nickname(self, event)
        await handle_event(self, event)

    # def _handle_response(self, response: Response) -> Any:
    #     if 200 <= response.status_code < 300:
    #         return response.content and json.loads(response.content)
    #     elif response.status_code == 400:
    #         raise BadRequestException(response)
    #     elif response.status_code == 401:
    #         raise UnauthorizedException(response)
    #     elif response.status_code == 403:
    #         raise ForbiddenException(response)
    #     elif response.status_code == 404:
    #         raise NotFoundException(response)
    #     elif response.status_code == 405:
    #         raise MethodNotAllowedException(response)
    #     elif response.status_code == 500:
    #         raise ApiNotImplementedException(response)
    #     else:
    #         raise ActionFailed(response)

    # async def _request(self, request: Request) -> Any:
    #     request.headers.update(self.get_authorization_header())
    #     request.json = {k: v for k, v in request.json.items() if v is not None} if request.json else None
    #     try:
    #         response = await self.adapter.request(request)
    #     except Exception as e:
    #         raise NetworkError("API request failed") from e

    #     return self._handle_response(response)

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> SendMessageResponse:
        if not isinstance(event, MessageEvent):
            raise RuntimeError("Event cannot be replied to!")
        if isinstance(message, str):
            message = Message(message)
        elif isinstance(message, MessageSegment):
            message = Message([message])
        elements = message.to_elements()
        return await self.send_message(contact=event.contact, elements=elements)

    @API
    async def send_message(
        self,
        *,
        contact: Contact,
        elements: List[Element],
    ) -> SendMessageResponse:
        """发送消息

        参数:
            contact: 要发送的目标
            message: 要发送的消息
        """
        message = MessageServiceStub(self.client)
        return await message.send_message(SendMessageRequest(contact=contact.dump(), elements=elements))

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
        message = MessageServiceStub(self.client)
        return await message.send_message_by_res_id(SendMessageByResIdRequest(res_id=res_id, contact=contact.dump()))
    

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
        message = MessageServiceStub(self.client)
        return await message.get_message(GetMessageRequest(message_id=message_id))
    
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
        message = MessageServiceStub(self.client)
        return await message.get_message_by_seq(GetMessageBySeqRequest(message_seq=message_seq))

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
        message = MessageServiceStub(self.client)
        return await message.get_history_message(GetHistoryMessageRequest(contact=contact.dump(), start_message_id=start_message_id, count=count))

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
        message = MessageServiceStub(self.client)
        return await message.recall_message(RecallMessageRequest(message_id=message_id))
    
    @API
    async def set_message_comment_emoji(
        self,
        *,
        contact: Contact,
        message_id: str,
        emoji: int,
        is_comment: bool = True,
    ):
        """给消息评论表情

        参数:
            contact: 要发送的目标
            message_id: 消息ID
            emoji: 表情
            is_comment: 是否评论, False为撤销评论
        """
        message = MessageServiceStub(self.client)
        return await message.react_message_with_emoji(ReactMessageWithEmojiRequest(contact=contact.dump(), message_id=message_id, face_id=emoji, is_comment=is_comment))
    

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
        message = MessageServiceStub(self.client)
        return await message.download_forward_message(DownloadForwardMessageRequest(res_id=res_id))
    
    @API
    async def delete_essence_message(
        self,
        *,
        group_id: int,
        message_id: str,
    ):
        """删除精华消息

        参数:
            group_id: 群ID
            message_id: 消息ID
        """
        message = MessageServiceStub(self.client)
        return await message.delete_essence_message(DeleteEssenceMessageRequest(group_id=group_id, message_id=message_id))
    
    @API
    async def get_esence_message_list(
        self,
        *,
        group_id: int,
    ):
        """获取精华消息列表

        参数:
            group_id: 群ID
        """
        message = MessageServiceStub(self.client)
        return (await message.get_essence_message_list(GetEssenceMessageListRequest(group_id=group_id))).messages
    
    @API
    async def set_essence_message(
        self,
        *,
        group_id: int,
        message_id: str,
    ):
        """设置精华消息

        参数:
            group_id: 群ID
            message_id: 消息ID
        """
        message = MessageServiceStub(self.client)
        return await message.set_essence_message(SetEssenceMessageRequest(group_id=group_id, message_id=message_id))