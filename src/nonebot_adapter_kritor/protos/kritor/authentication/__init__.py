# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: auth/authentication.proto
# plugin: python-betterproto
# This file has been @generated

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

import grpclib
import betterproto
from betterproto.grpc.grpclib_server import ServiceBase

if TYPE_CHECKING:
    import grpclib.server
    from grpclib.metadata import Deadline
    from betterproto.grpc.grpclib_client import MetadataLike


class TicketOperationResponseCode(betterproto.Enum):
    OK = 0
    ERROR = 1


class AuthenticateResponseAuthenticateResponseCode(betterproto.Enum):
    OK = 0
    NO_ACCOUNT = 1
    NO_TICKET = 2
    LOGIC_ERROR = 3


@dataclass(eq=False, repr=False)
class AuthenticateRequest(betterproto.Message):
    """在某个账号授权成功之后，接下来所有的请求都必须围绕该账号，且禁止再次发送授权包。"""

    account: str = betterproto.string_field(1)
    ticket: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class AuthenticateResponse(betterproto.Message):
    code: "AuthenticateResponseAuthenticateResponseCode" = betterproto.enum_field(1)
    msg: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class GetAuthenticationStateRequest(betterproto.Message):
    account: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GetAuthenticationStateResponse(betterproto.Message):
    is_required: bool = betterproto.bool_field(1)


@dataclass(eq=False, repr=False)
class GetTicketRequest(betterproto.Message):
    account: str = betterproto.string_field(1)
    ticket: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class GetTicketResponse(betterproto.Message):
    code: "TicketOperationResponseCode" = betterproto.enum_field(1)
    msg: str = betterproto.string_field(2)
    tickets: List[str] = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class AddTicketRequest(betterproto.Message):
    account: str = betterproto.string_field(1)
    ticket: str = betterproto.string_field(2)
    new_ticket: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class AddTicketResponse(betterproto.Message):
    code: "TicketOperationResponseCode" = betterproto.enum_field(1)
    msg: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class DeleteTicketRequest(betterproto.Message):
    account: str = betterproto.string_field(1)
    ticket: str = betterproto.string_field(2)
    delete_ticket: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class DeleteTicketResponse(betterproto.Message):
    code: "TicketOperationResponseCode" = betterproto.enum_field(1)
    msg: str = betterproto.string_field(2)


class AuthenticationServiceStub(betterproto.ServiceStub):
    async def authenticate(
        self,
        authenticate_request: "AuthenticateRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "AuthenticateResponse":
        return await self._unary_unary(
            "/kritor.authentication.AuthenticationService/Authenticate",
            authenticate_request,
            AuthenticateResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_authentication_state(
        self,
        get_authentication_state_request: "GetAuthenticationStateRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GetAuthenticationStateResponse":
        return await self._unary_unary(
            "/kritor.authentication.AuthenticationService/GetAuthenticationState",
            get_authentication_state_request,
            GetAuthenticationStateResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_ticket(
        self,
        get_ticket_request: "GetTicketRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GetTicketResponse":
        return await self._unary_unary(
            "/kritor.authentication.AuthenticationService/GetTicket",
            get_ticket_request,
            GetTicketResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def delete_ticket(
        self,
        delete_ticket_request: "DeleteTicketRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "DeleteTicketResponse":
        return await self._unary_unary(
            "/kritor.authentication.AuthenticationService/DeleteTicket",
            delete_ticket_request,
            DeleteTicketResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def add_ticket(
        self,
        add_ticket_request: "AddTicketRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "AddTicketResponse":
        return await self._unary_unary(
            "/kritor.authentication.AuthenticationService/AddTicket",
            add_ticket_request,
            AddTicketResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class AuthenticationServiceBase(ServiceBase):

    async def authenticate(self, authenticate_request: "AuthenticateRequest") -> "AuthenticateResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_authentication_state(
        self, get_authentication_state_request: "GetAuthenticationStateRequest"
    ) -> "GetAuthenticationStateResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_ticket(self, get_ticket_request: "GetTicketRequest") -> "GetTicketResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def delete_ticket(self, delete_ticket_request: "DeleteTicketRequest") -> "DeleteTicketResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def add_ticket(self, add_ticket_request: "AddTicketRequest") -> "AddTicketResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_authenticate(
        self, stream: "grpclib.server.Stream[AuthenticateRequest, AuthenticateResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.authenticate(request)
        await stream.send_message(response)

    async def __rpc_get_authentication_state(
        self,
        stream: "grpclib.server.Stream[GetAuthenticationStateRequest, GetAuthenticationStateResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_authentication_state(request)
        await stream.send_message(response)

    async def __rpc_get_ticket(self, stream: "grpclib.server.Stream[GetTicketRequest, GetTicketResponse]") -> None:
        request = await stream.recv_message()
        response = await self.get_ticket(request)
        await stream.send_message(response)

    async def __rpc_delete_ticket(
        self, stream: "grpclib.server.Stream[DeleteTicketRequest, DeleteTicketResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.delete_ticket(request)
        await stream.send_message(response)

    async def __rpc_add_ticket(self, stream: "grpclib.server.Stream[AddTicketRequest, AddTicketResponse]") -> None:
        request = await stream.recv_message()
        response = await self.add_ticket(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/kritor.authentication.AuthenticationService/Authenticate": grpclib.const.Handler(
                self.__rpc_authenticate,
                grpclib.const.Cardinality.UNARY_UNARY,
                AuthenticateRequest,
                AuthenticateResponse,
            ),
            "/kritor.authentication.AuthenticationService/GetAuthenticationState": grpclib.const.Handler(
                self.__rpc_get_authentication_state,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetAuthenticationStateRequest,
                GetAuthenticationStateResponse,
            ),
            "/kritor.authentication.AuthenticationService/GetTicket": grpclib.const.Handler(
                self.__rpc_get_ticket,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetTicketRequest,
                GetTicketResponse,
            ),
            "/kritor.authentication.AuthenticationService/DeleteTicket": grpclib.const.Handler(
                self.__rpc_delete_ticket,
                grpclib.const.Cardinality.UNARY_UNARY,
                DeleteTicketRequest,
                DeleteTicketResponse,
            ),
            "/kritor.authentication.AuthenticationService/AddTicket": grpclib.const.Handler(
                self.__rpc_add_ticket,
                grpclib.const.Cardinality.UNARY_UNARY,
                AddTicketRequest,
                AddTicketResponse,
            ),
        }
