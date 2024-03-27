from typing import Optional

from nonebot.drivers import Response
from nonebot.exception import AdapterException
from nonebot.exception import ActionFailed as BaseActionFailed
from nonebot.exception import NetworkError as BaseNetworkError
from nonebot.exception import ApiNotAvailable as BaseApiNotAvailable


class KritorAdapterException(AdapterException):
    def __init__(self):
        super().__init__("kritor")


class ActionFailed(BaseActionFailed, KritorAdapterException):
    def __init__(self, response: Response):
        self.status_code: int = response.status_code
        self.headers = response.headers
        self.content = response.content

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: {self.status_code}, headers={self.headers}, content={self.content}>"
        )

    def __str__(self):
        return self.__repr__()


class BadRequestException(ActionFailed):
    pass


class UnauthorizedException(ActionFailed):
    pass


class ForbiddenException(ActionFailed):
    pass


class NotFoundException(ActionFailed):
    pass


class MethodNotAllowedException(ActionFailed):
    pass


class ApiNotImplementedException(ActionFailed):
    pass


class NetworkError(BaseNetworkError, KritorAdapterException):
    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg: Optional[str] = msg
        """错误原因"""

    def __repr__(self):
        return f"<NetWorkError message={self.msg}>"

    def __str__(self):
        return self.__repr__()


class ApiNotAvailable(BaseApiNotAvailable, KritorAdapterException):
    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg: Optional[str] = msg
        """错误原因"""
