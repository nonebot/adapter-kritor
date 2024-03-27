import json
import asyncio
from typing_extensions import override
from typing import Any, Dict, List, Literal, Optional

from nonebot.utils import escape_tag
from nonebot.compat import PYDANTIC_V2, model_dump, type_validate_python
from nonebot.drivers import Driver

from nonebot import get_plugin_config
from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .utils import API, log
from .config import Config, ClientInfo
from .exception import ApiNotAvailable

from grpclib.client import Channel
from betterproto import which_one_of, Casing
from .protos.kritor.authentication import AuthenticateRequest, AuthenticationServiceStub, AuthenticateResponseAuthenticateResponseCode
from .protos.kritor.event import EventServiceStub, RequestPushEvent, EventType
from .event import MessageEventType
class Adapter(BaseAdapter):
    bots: Dict[str, Bot]

    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        # 读取适配器所需的配置项
        self.kritor_config: Config = get_plugin_config(Config)
        self.tasks: List[asyncio.Task] = []  # 存储 连接 任务
        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
        """适配器名称"""
        return "Kritor"

    def setup(self) -> None:
        # 在 NoneBot 启动和关闭时进行相关操作
        self.on_ready(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def startup(self) -> None:
        """定义启动时的操作，例如和平台建立连接"""
        for client in self.kritor_config.kritor_clients:
            self.tasks.append(asyncio.create_task(self.grpc(client)))

    async def shutdown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(
            *(asyncio.wait_for(task, timeout=10) for task in self.tasks),
            return_exceptions=True,
        )


    async def _listen_message(self, bot: Bot, service: EventServiceStub):
        async for event in service.register_active_listener(RequestPushEvent(EventType.EVENT_TYPE_MESSAGE)):
            log("DEBUG", f"Received message event: {event.message}")
            message = event.message
            event = type_validate_python(MessageEventType, message.to_pydict(casing=Casing.SNAKE))  # type: ignore
            asyncio.create_task(bot.handle_event(event))

    async def _listen_notice(self, bot: Bot, service: EventServiceStub):
        async for event in service.register_active_listener(RequestPushEvent(EventType.EVENT_TYPE_NOTICE)):
            notice = which_one_of(event.notice, "notice")
            log("DEBUG", f"Received notice event {notice[0]}: {notice[1]}")

    async def _listen_request(self, bot: Bot, service: EventServiceStub):
        async for event in service.register_active_listener(RequestPushEvent(EventType.EVENT_TYPE_REQUEST)):
            request = which_one_of(event.request, "request")
            log("DEBUG", f"Received request event {request[0]}: {request[1]}")

    async def _listen_core(self, bot: Bot, service: EventServiceStub):
        async for event in service.register_active_listener(RequestPushEvent(EventType.EVENT_TYPE_CORE_EVENT)):
            log("DEBUG", f"Received event: {event}")

    async def grpc(self, info: ClientInfo) -> None:
        channel = Channel(info.host, info.port)
        async with channel:
            auth = AuthenticationServiceStub(channel)
            request = AuthenticateRequest(account=info.account, ticket=info.ticket)
            response = await auth.authenticate(request)
            if response.code != AuthenticateResponseAuthenticateResponseCode.OK:
                log(
                    "ERROR", 
                    f"<r><bg #f8bbd0>Account {info.account} authenticate failed\n"
                    f"Error code: {response.code}"
                    f"Error message: {response.msg}</bg #f8bbd0></r>"
                )
                return
            log(
                "INFO",
                f"<y>Account {info.account} authenticate success</y>"
            )
            bot = Bot(self, info.account, info, channel)
            self.bot_connect(bot)
            event = EventServiceStub(channel)
            listens = [
                asyncio.create_task(self._listen_message(bot, event)),
                asyncio.create_task(self._listen_notice(bot, event)),
                asyncio.create_task(self._listen_request(bot, event)),
                asyncio.create_task(self._listen_core(bot, event))
            ]
            await asyncio.wait(listens, return_when=asyncio.FIRST_EXCEPTION)
        for task in listens:
            task.cancel()
            await task
        self.bot_disconnect(bot)

    # @staticmethod
    # def payload_to_event(payload: SatoriEvent) -> Event:
    #     EventClass = EVENT_CLASSES.get(payload.type, None)
    #     if EventClass is None:
    #         log("WARNING", f"Unknown payload type: {payload.type}")
    #         event = type_validate_python(Event, model_dump(payload))
    #         event.__type__ = payload.type  # type: ignore
    #         return event
    #     return type_validate_python(EventClass, model_dump(payload))

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        log("DEBUG", f"Bot {bot.self_id} calling API <y>{api}</y>")
        api_handler: Optional[API] = getattr(bot.__class__, api, None)
        if api_handler is None:
            raise ApiNotAvailable(api)
        return await api_handler(bot, **data)
