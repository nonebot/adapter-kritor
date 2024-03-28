from typing import Literal, Optional

from grpclib import GRPCError
from nonebot.exception import AdapterException
from nonebot.exception import ActionFailed as BaseActionFailed
from nonebot.exception import ApiNotAvailable as BaseApiNotAvailable


class KritorAdapterException(AdapterException):
    def __init__(self):
        super().__init__("kritor")


class ActionFailed(BaseActionFailed, KritorAdapterException):
    def __init__(self, error: GRPCError):
        self.status_code = error.status.value
        self.message = error.message
        self.details = error.details

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.status_code}, message={self.message}, details={self.details}>"

    def __str__(self):
        return self.__repr__()


class CancelledError(ActionFailed):
    status_code: Literal[1] = 1


class Unknown(ActionFailed):
    status_code: Literal[2] = 2


class InvalidArgument(ActionFailed):
    status_code: Literal[3] = 3


class DeadlineExceeded(ActionFailed):
    status_code: Literal[4] = 4


class NotFound(ActionFailed):
    status_code: Literal[5] = 5


class AlreadyExists(ActionFailed):
    status_code: Literal[6] = 6


class PermissionDenied(ActionFailed):
    status_code: Literal[7] = 7


class ResourceExhausted(ActionFailed):
    status_code: Literal[8] = 8


class FailedPrecondition(ActionFailed):
    status_code: Literal[9] = 9


class Aborted(ActionFailed):
    status_code: Literal[10] = 10


class OutOfRange(ActionFailed):
    status_code: Literal[11] = 11


class Unimplemented(ActionFailed):
    status_code: Literal[12] = 12


class Internal(ActionFailed):
    status_code: Literal[13] = 13


class Unavailable(ActionFailed):
    status_code: Literal[14] = 14


class DataLoss(ActionFailed):
    status_code: Literal[15] = 15


class Unauthenticated(ActionFailed):
    status_code: Literal[16] = 16


class ApiNotAvailable(BaseApiNotAvailable, KritorAdapterException):
    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg: Optional[str] = msg
        """错误原因"""


STATUS_CODE_TO_EXCEPTION = {
    1: CancelledError,
    2: Unknown,
    3: InvalidArgument,
    4: DeadlineExceeded,
    5: NotFound,
    6: AlreadyExists,
    7: PermissionDenied,
    8: ResourceExhausted,
    9: FailedPrecondition,
    10: Aborted,
    11: OutOfRange,
    12: Unimplemented,
    13: Internal,
    14: Unavailable,
    15: DataLoss,
    16: Unauthenticated,
}
