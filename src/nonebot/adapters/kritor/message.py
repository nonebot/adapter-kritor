from io import BytesIO
from pathlib import Path
from collections.abc import Iterable
from dataclasses import field, dataclass
from typing_extensions import NotRequired, override
from typing import Union, Literal, ClassVar, Optional, TypedDict

from betterproto import Casing, which_one_of

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .model import SceneType
from .protos.kritor.common import Scene as KritorScene
from .protos.kritor.common import (
    Button,
    Element,
    KeyboardRow,
    ContactElement,
    KeyboardElement,
    ElementElementType,
    ImageElementImageType,
    MusicElementMusicPlatform,
)


class MessageSegment(BaseMessageSegment["Message"]):
    __element_type__: ClassVar[ElementElementType]

    def __init_subclass__(cls, **kwargs):
        if "element_type" in kwargs:
            cls.__element_type__ = kwargs["element_type"]

    @classmethod
    @override
    def get_message_class(cls) -> type["Message"]:
        # 返回适配器的 Message 类型本身
        return Message

    @classmethod
    def parse(cls, element: Element):
        name, data = which_one_of(element, "data")
        return cls(name, data.to_pydict(casing=Casing.SNAKE) if data else {})  # type: ignore

    def dump(self) -> "Element":
        return Element().from_pydict({"type": self.__element_type__, self.type: self.data})

    @override
    def __str__(self) -> str:
        shown_data = {k: v for k, v in self.data.items() if not k.startswith("_")}
        # 返回该消息段的纯文本表现形式，通常在日志中展示
        return self.data["text"] if self.is_text() else f"[{self.type}: {shown_data}]"

    @override
    def is_text(self) -> bool:
        # 判断该消息段是否为纯文本
        return self.type == "text"

    @staticmethod
    def text(content: str) -> "Text":
        return Text("text", {"text": content})

    @staticmethod
    def at(uid: str) -> "At":
        return At("at", {"uid": uid})

    @staticmethod
    def atall() -> "At":
        return At("at", {"uid": "all"})

    @staticmethod
    def face(fid: int, is_big: bool = False) -> "Face":
        return Face("face", {"id": fid, "is_big": is_big})

    @staticmethod
    def bubble_face(fid: int, count: int) -> "BubbleFace":
        return BubbleFace("buble_face", {"id": fid, "count": count})

    @staticmethod
    def reply(message_id: str) -> "Reply":
        return Reply("reply", {"message_id": message_id})

    @staticmethod
    def image(
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        raw: Optional[Union[bytes, BytesIO]] = None,
    ) -> "Image":
        if url:
            return Image("image", {"file_url": url})
        if path:
            file = Path(path).resolve().absolute()
            return Image("image", {"file_path": str(file), "file_name": file.name})
        if raw:
            return Image("image", {"file": raw if isinstance(raw, bytes) else raw.getvalue()})
        raise ValueError("image need at least one of url, path and raw")

    @staticmethod
    def voice(
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        raw: Optional[Union[bytes, BytesIO]] = None,
    ) -> "Voice":
        if url:
            return Voice("voice", {"file_url": url})
        if path:
            file = Path(path).resolve().absolute()
            return Voice("voice", {"file_path": str(file), "file_name": file.name})
        if raw:
            return Voice("voice", {"file": raw if isinstance(raw, bytes) else raw.getvalue()})
        raise ValueError("voice need at least one of url, path and raw")

    @staticmethod
    def video(
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        raw: Optional[Union[bytes, BytesIO]] = None,
    ) -> "Video":
        if url:
            return Video("video", {"file_url": url})
        if path:
            file = Path(path).resolve().absolute()
            return Video("video", {"file_path": str(file), "file_name": file.name})
        if raw:
            return Video("video", {"file": raw if isinstance(raw, bytes) else raw.getvalue()})
        raise ValueError("video need at least one of url, path and raw")

    @staticmethod
    def basketball(id_: int) -> "Basketball":
        """投篮"""
        return Basketball("basketball", {"id": id_})

    @staticmethod
    def rps(id_: int) -> "Rps":
        """石头剪刀布"""
        return Rps("rps", {"id": id_})

    @staticmethod
    def dice(id_: int) -> "Dice":
        """骰子"""
        return Dice("dice", {"id": id_})

    @staticmethod
    def poke(id_: int, type_: int, strength: int) -> "Poke":
        """戳一戳，即带有窗口抖动效果的消息

        请务必与双击头像功能区分。

        Args:
            id_: 戳一戳 id
            type_: 戳一戳类型
            strength: 戳一戳强度
        """
        return Poke("poke", {"id": id_, "poke_type": type_, "strength": strength})

    @staticmethod
    def music(
        platform: Literal["qq", "netease", "custom"], url: str, audio_url: str, title: str, author: str, pic_url: str
    ) -> "Music":
        _platform = (
            MusicElementMusicPlatform.QQ
            if platform == "qq"
            else MusicElementMusicPlatform.NETEASE if platform == "netease" else MusicElementMusicPlatform.CUSTOM
        )
        return Music(
            "music",
            {
                "platform": _platform,
                "custom": {"url": url, "audio": audio_url, "title": title, "author": author, "pic": pic_url},
            },
        )

    @staticmethod
    def weather(city: str, code: str) -> "Weather":
        return Weather("weather", {"city": city, "code": code})

    @staticmethod
    def location(lat: float, lon: float, title: str, content: str) -> "Location":
        return Location("location", {"lat": lat, "lon": lon, "title": title, "content": content})

    @staticmethod
    def share(url: str, title: str, content: str, image_url: str) -> "Share":
        return Share("share", {"url": url, "title": title, "content": content, "image": image_url})

    @staticmethod
    def market_face(id_: str) -> "MarketFace":
        return MarketFace("market_face", {"id": id_})

    @staticmethod
    def forward(res_id: str, uniseq: str, summary: str, description: str) -> "Forward":
        return Forward("forward", {"res_id": res_id, "uniseq": uniseq, "summary": summary, "description": description})

    @staticmethod
    def contact(type_: SceneType, id_: str) -> "Contact":
        return Contact("contact", {"type": type_, "id": id_})

    @staticmethod
    def json(json: str) -> "Json":
        return Json("json", {"json": json})

    @staticmethod
    def xml(xml: str) -> "Xml":
        return Xml("xml", {"xml": xml})

    @staticmethod
    def markdown(markdown: str) -> "Markdown":
        return Markdown("markdown", {"markdown": markdown})

    @staticmethod
    def keyboard(bot_appid: int, buttons: list[list[Button]]) -> "Keyboard":
        return Keyboard("keyboard", {"bot_appid": bot_appid, "rows": [{"buttons": row} for row in buttons]})


class TextData(TypedDict):
    text: str


@dataclass
class Text(MessageSegment, element_type=ElementElementType.TEXT):
    data: TextData = field(default_factory=dict)  # type: ignore


class AtData(TypedDict):
    uid: str  # "all" if at_all
    uin: NotRequired[int]


@dataclass
class At(MessageSegment, element_type=ElementElementType.AT):
    data: AtData = field(default_factory=dict)  # type: ignore


class FaceData(TypedDict):
    id: int
    is_big: NotRequired[bool]
    result: NotRequired[int]


@dataclass
class Face(MessageSegment, element_type=ElementElementType.FACE):
    data: FaceData = field(default_factory=dict)  # type: ignore


class BubbleFaceData(TypedDict):
    id: int
    count: int


@dataclass
class BubbleFace(MessageSegment, element_type=ElementElementType.BUBBLE_FACE):
    data: BubbleFaceData = field(default_factory=dict)  # type: ignore


class ReplyData(TypedDict):
    message_id: str


@dataclass
class Reply(MessageSegment, element_type=ElementElementType.REPLY):
    data: ReplyData = field(default_factory=dict)  # type: ignore


class ImageData(TypedDict):
    file: NotRequired[bytes]
    file_name: NotRequired[str]
    file_path: NotRequired[str]
    file_url: NotRequired[str]
    file_md5: NotRequired[str]
    file_type: NotRequired[ImageElementImageType]
    sub_type: NotRequired[int]


@dataclass
class Image(MessageSegment, element_type=ElementElementType.IMAGE):
    data: ImageData = field(default_factory=dict)  # type: ignore


class VoiceData(TypedDict):
    file: NotRequired[bytes]
    file_name: NotRequired[str]
    file_path: NotRequired[str]
    file_url: NotRequired[str]
    file_md5: NotRequired[str]
    magic: NotRequired[bool]


@dataclass
class Voice(MessageSegment, element_type=ElementElementType.VOICE):
    data: VoiceData = field(default_factory=dict)  # type: ignore


class VideoData(TypedDict):
    file: NotRequired[bytes]
    file_name: NotRequired[str]
    file_path: NotRequired[str]
    file_url: NotRequired[str]
    file_md5: NotRequired[str]


@dataclass
class Video(MessageSegment, element_type=ElementElementType.VIDEO):
    data: VideoData = field(default_factory=dict)  # type: ignore


class RandomFaceData(TypedDict):
    id: int


@dataclass
class Basketball(MessageSegment, element_type=ElementElementType.BASKETBALL):
    data: RandomFaceData = field(default_factory=dict)  # type: ignore


@dataclass
class Rps(MessageSegment, element_type=ElementElementType.RPS):
    data: RandomFaceData = field(default_factory=dict)  # type: ignore


@dataclass
class Dice(MessageSegment, element_type=ElementElementType.DICE):
    data: RandomFaceData = field(default_factory=dict)  # type: ignore


class PokeData(TypedDict):
    id: int
    poke_type: int
    strength: int


@dataclass
class Poke(MessageSegment, element_type=ElementElementType.POKE):
    data: PokeData = field(default_factory=dict)  # type: ignore


class CustomMusicData(TypedDict):
    url: str
    audio: str
    title: str
    author: str
    pic: str


class MusicData(TypedDict):
    platform: MusicElementMusicPlatform
    id: NotRequired[str]
    custom: NotRequired[CustomMusicData]


@dataclass
class Music(MessageSegment, element_type=ElementElementType.MUSIC):
    data: MusicData = field(default_factory=dict)  # type: ignore


class WeatherData(TypedDict):
    city: str
    code: str


@dataclass
class Weather(MessageSegment, element_type=ElementElementType.WEATHER):
    data: WeatherData = field(default_factory=dict)  # type: ignore


class LocationData(TypedDict):
    lat: float
    lon: float
    title: str
    content: str


@dataclass
class Location(MessageSegment, element_type=ElementElementType.LOCATION):
    data: LocationData = field(default_factory=dict)  # type: ignore


class ShareData(TypedDict):
    url: str
    title: str
    content: str
    image: str


@dataclass
class Share(MessageSegment, element_type=ElementElementType.SHARE):
    data: ShareData = field(default_factory=dict)  # type: ignore


class GiftData(TypedDict):
    qq: int
    id: int


@dataclass
class Gift(MessageSegment, element_type=ElementElementType.GIFT):
    data: GiftData = field(default_factory=dict)  # type: ignore


class MarketFaceData(TypedDict):
    id: str


@dataclass
class MarketFace(MessageSegment, element_type=ElementElementType.MARKET_FACE):
    data: MarketFaceData = field(default_factory=dict)  # type: ignore


class ForwardData(TypedDict):
    res_id: str
    uniseq: str
    summary: str
    description: str


@dataclass
class Forward(MessageSegment, element_type=ElementElementType.FORWARD):
    data: ForwardData = field(default_factory=dict)  # type: ignore


class ContactData(TypedDict):
    type: SceneType
    id: str


@dataclass
class Contact(MessageSegment, element_type=ElementElementType.CONTACT):
    data: ContactData = field(default_factory=dict)  # type: ignore

    @classmethod
    @override
    def parse(cls, element: Element):
        if element.type == ElementElementType.CONTACT:
            data = element.contact
            return cls("contact", {"type": SceneType(data.scene.value), "id": data.peer})
        raise ValueError(f"Unexpected element type: {element.type}")

    @override
    def dump(self) -> "Element":
        return Element(
            type=ElementElementType.CONTACT,
            contact=ContactElement(scene=KritorScene(self.data["type"].value), peer=self.data["id"]),
        )


class JsonData(TypedDict):
    json: str


@dataclass
class Json(MessageSegment, element_type=ElementElementType.JSON):
    data: JsonData = field(default_factory=dict)  # type: ignore


class XmlData(TypedDict):
    xml: str


@dataclass
class Xml(MessageSegment, element_type=ElementElementType.XML):
    data: XmlData = field(default_factory=dict)  # type: ignore


class FileData(TypedDict):
    name: NotRequired[str]
    size: NotRequired[int]
    expire_time: NotRequired[int]
    id: NotRequired[str]
    url: NotRequired[str]
    biz: NotRequired[int]
    sub_id: NotRequired[str]


@dataclass
class File(MessageSegment, element_type=ElementElementType.FILE):
    data: FileData = field(default_factory=dict)  # type: ignore


class MarkdownData(TypedDict):
    markdown: str


@dataclass
class Markdown(MessageSegment, element_type=ElementElementType.MARKDOWN):
    data: MarkdownData = field(default_factory=dict)  # type: ignore


class KeyboardRowData(TypedDict):
    buttons: list[Button]


class KeyboardData(TypedDict):
    rows: list[KeyboardRowData]
    bot_appid: int


@dataclass
class Keyboard(MessageSegment, element_type=ElementElementType.KEYBOARD):
    data: KeyboardData = field(default_factory=dict)  # type: ignore

    @override
    def dump(self) -> "Element":
        return Element(
            type=ElementElementType.KEYBOARD,
            keyboard=KeyboardElement(
                rows=[KeyboardRow(buttons=row["buttons"]) for row in self.data["rows"]],
                bot_appid=self.data["bot_appid"],
            ),
        )


TYPE_MAPPING = {cls.__element_type__: cls for cls in MessageSegment.__subclasses__()}  # type: ignore


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override
    def get_segment_class(cls) -> type[MessageSegment]:
        # 返回适配器的 MessageSegment 类型本身
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment.text(msg)

    @classmethod
    def from_elements(cls, elements: list[Element]) -> "Message":
        msg = Message()
        for element in elements:
            msg.append(TYPE_MAPPING[element.type].parse(element))
        return msg

    def to_elements(self) -> list[Element]:
        res = []
        for seg in self:
            res.append(seg.dump())
        return res
