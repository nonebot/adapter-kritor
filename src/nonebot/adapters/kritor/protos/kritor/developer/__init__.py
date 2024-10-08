# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: developer/developer.proto, developer/qsign.proto
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


@dataclass(eq=False, repr=False)
class ShellRequest(betterproto.Message):
    command: List[str] = betterproto.string_field(1)
    directory: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ShellResponse(betterproto.Message):
    is_success: bool = betterproto.bool_field(1)
    data: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class GetLogRequest(betterproto.Message):
    start: int = betterproto.uint64_field(1)
    recent: bool = betterproto.bool_field(2)


@dataclass(eq=False, repr=False)
class GetLogResponse(betterproto.Message):
    is_success: bool = betterproto.bool_field(1)
    log: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ClearCacheRequest(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class ClearCacheResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class GetDeviceBatteryRequest(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class GetDeviceBatteryResponse(betterproto.Message):
    battery: int = betterproto.uint32_field(1)
    scale: int = betterproto.uint32_field(2)
    status: int = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class UploadImageRequest(betterproto.Message):
    file: bytes = betterproto.bytes_field(1, group="data")
    file_name: str = betterproto.string_field(2, group="data")
    file_path: str = betterproto.string_field(3, group="data")
    file_url: str = betterproto.string_field(4, group="data")
    group_id: int = betterproto.uint64_field(5)


@dataclass(eq=False, repr=False)
class UploadImageResponse(betterproto.Message):
    is_success: bool = betterproto.bool_field(1)
    image_url: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class SendPacketRequest(betterproto.Message):
    command: str = betterproto.string_field(1)
    request_buffer: bytes = betterproto.bytes_field(2)
    is_protobuf: bool = betterproto.bool_field(3)
    attrs: Dict[str, str] = betterproto.map_field(4, betterproto.TYPE_STRING, betterproto.TYPE_STRING)


@dataclass(eq=False, repr=False)
class SendPacketResponse(betterproto.Message):
    is_success: bool = betterproto.bool_field(1)
    response_buffer: bytes = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class SignRequest(betterproto.Message):
    uin: str = betterproto.string_field(1)
    command: str = betterproto.string_field(2)
    seq: int = betterproto.uint32_field(3)
    buffer: bytes = betterproto.bytes_field(4)
    qua: Optional[str] = betterproto.string_field(6, optional=True)


@dataclass(eq=False, repr=False)
class SignResponse(betterproto.Message):
    sec_sig: bytes = betterproto.bytes_field(1)
    sec_device_token: bytes = betterproto.bytes_field(2)
    sec_extra: bytes = betterproto.bytes_field(3)


@dataclass(eq=False, repr=False)
class EnergyRequest(betterproto.Message):
    data: str = betterproto.string_field(2)
    salt: bytes = betterproto.bytes_field(3)


@dataclass(eq=False, repr=False)
class EnergyResponse(betterproto.Message):
    result: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class GetCmdWhitelistRequest(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class GetCmdWhitelistResponse(betterproto.Message):
    commands: List[str] = betterproto.string_field(1)


class DeveloperServiceStub(betterproto.ServiceStub):
    async def shell(
        self,
        shell_request: "ShellRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "ShellResponse":
        return await self._unary_unary(
            "/kritor.developer.DeveloperService/Shell",
            shell_request,
            ShellResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_log(
        self,
        get_log_request: "GetLogRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GetLogResponse":
        return await self._unary_unary(
            "/kritor.developer.DeveloperService/GetLog",
            get_log_request,
            GetLogResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def clear_cache(
        self,
        clear_cache_request: "ClearCacheRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "ClearCacheResponse":
        return await self._unary_unary(
            "/kritor.developer.DeveloperService/ClearCache",
            clear_cache_request,
            ClearCacheResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_device_battery(
        self,
        get_device_battery_request: "GetDeviceBatteryRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GetDeviceBatteryResponse":
        return await self._unary_unary(
            "/kritor.developer.DeveloperService/GetDeviceBattery",
            get_device_battery_request,
            GetDeviceBatteryResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def upload_image(
        self,
        upload_image_request: "UploadImageRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "UploadImageResponse":
        return await self._unary_unary(
            "/kritor.developer.DeveloperService/UploadImage",
            upload_image_request,
            UploadImageResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def send_packet(
        self,
        send_packet_request: "SendPacketRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "SendPacketResponse":
        return await self._unary_unary(
            "/kritor.developer.DeveloperService/SendPacket",
            send_packet_request,
            SendPacketResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class QsignServiceStub(betterproto.ServiceStub):
    async def sign(
        self,
        sign_request: "SignRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "SignResponse":
        return await self._unary_unary(
            "/kritor.developer.QsignService/Sign",
            sign_request,
            SignResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def energy(
        self,
        energy_request: "EnergyRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "EnergyResponse":
        return await self._unary_unary(
            "/kritor.developer.QsignService/Energy",
            energy_request,
            EnergyResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_cmd_whitelist(
        self,
        get_cmd_whitelist_request: "GetCmdWhitelistRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GetCmdWhitelistResponse":
        return await self._unary_unary(
            "/kritor.developer.QsignService/GetCmdWhitelist",
            get_cmd_whitelist_request,
            GetCmdWhitelistResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class DeveloperServiceBase(ServiceBase):

    async def shell(self, shell_request: "ShellRequest") -> "ShellResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_log(self, get_log_request: "GetLogRequest") -> "GetLogResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def clear_cache(self, clear_cache_request: "ClearCacheRequest") -> "ClearCacheResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_device_battery(
        self, get_device_battery_request: "GetDeviceBatteryRequest"
    ) -> "GetDeviceBatteryResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def upload_image(self, upload_image_request: "UploadImageRequest") -> "UploadImageResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def send_packet(self, send_packet_request: "SendPacketRequest") -> "SendPacketResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_shell(self, stream: "grpclib.server.Stream[ShellRequest, ShellResponse]") -> None:
        request = await stream.recv_message()
        response = await self.shell(request)
        await stream.send_message(response)

    async def __rpc_get_log(self, stream: "grpclib.server.Stream[GetLogRequest, GetLogResponse]") -> None:
        request = await stream.recv_message()
        response = await self.get_log(request)
        await stream.send_message(response)

    async def __rpc_clear_cache(self, stream: "grpclib.server.Stream[ClearCacheRequest, ClearCacheResponse]") -> None:
        request = await stream.recv_message()
        response = await self.clear_cache(request)
        await stream.send_message(response)

    async def __rpc_get_device_battery(
        self,
        stream: "grpclib.server.Stream[GetDeviceBatteryRequest, GetDeviceBatteryResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_device_battery(request)
        await stream.send_message(response)

    async def __rpc_upload_image(
        self, stream: "grpclib.server.Stream[UploadImageRequest, UploadImageResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.upload_image(request)
        await stream.send_message(response)

    async def __rpc_send_packet(self, stream: "grpclib.server.Stream[SendPacketRequest, SendPacketResponse]") -> None:
        request = await stream.recv_message()
        response = await self.send_packet(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/kritor.developer.DeveloperService/Shell": grpclib.const.Handler(
                self.__rpc_shell,
                grpclib.const.Cardinality.UNARY_UNARY,
                ShellRequest,
                ShellResponse,
            ),
            "/kritor.developer.DeveloperService/GetLog": grpclib.const.Handler(
                self.__rpc_get_log,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetLogRequest,
                GetLogResponse,
            ),
            "/kritor.developer.DeveloperService/ClearCache": grpclib.const.Handler(
                self.__rpc_clear_cache,
                grpclib.const.Cardinality.UNARY_UNARY,
                ClearCacheRequest,
                ClearCacheResponse,
            ),
            "/kritor.developer.DeveloperService/GetDeviceBattery": grpclib.const.Handler(
                self.__rpc_get_device_battery,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetDeviceBatteryRequest,
                GetDeviceBatteryResponse,
            ),
            "/kritor.developer.DeveloperService/UploadImage": grpclib.const.Handler(
                self.__rpc_upload_image,
                grpclib.const.Cardinality.UNARY_UNARY,
                UploadImageRequest,
                UploadImageResponse,
            ),
            "/kritor.developer.DeveloperService/SendPacket": grpclib.const.Handler(
                self.__rpc_send_packet,
                grpclib.const.Cardinality.UNARY_UNARY,
                SendPacketRequest,
                SendPacketResponse,
            ),
        }


class QsignServiceBase(ServiceBase):

    async def sign(self, sign_request: "SignRequest") -> "SignResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def energy(self, energy_request: "EnergyRequest") -> "EnergyResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_cmd_whitelist(self, get_cmd_whitelist_request: "GetCmdWhitelistRequest") -> "GetCmdWhitelistResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_sign(self, stream: "grpclib.server.Stream[SignRequest, SignResponse]") -> None:
        request = await stream.recv_message()
        response = await self.sign(request)
        await stream.send_message(response)

    async def __rpc_energy(self, stream: "grpclib.server.Stream[EnergyRequest, EnergyResponse]") -> None:
        request = await stream.recv_message()
        response = await self.energy(request)
        await stream.send_message(response)

    async def __rpc_get_cmd_whitelist(
        self,
        stream: "grpclib.server.Stream[GetCmdWhitelistRequest, GetCmdWhitelistResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_cmd_whitelist(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/kritor.developer.QsignService/Sign": grpclib.const.Handler(
                self.__rpc_sign,
                grpclib.const.Cardinality.UNARY_UNARY,
                SignRequest,
                SignResponse,
            ),
            "/kritor.developer.QsignService/Energy": grpclib.const.Handler(
                self.__rpc_energy,
                grpclib.const.Cardinality.UNARY_UNARY,
                EnergyRequest,
                EnergyResponse,
            ),
            "/kritor.developer.QsignService/GetCmdWhitelist": grpclib.const.Handler(
                self.__rpc_get_cmd_whitelist,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetCmdWhitelistRequest,
                GetCmdWhitelistResponse,
            ),
        }
