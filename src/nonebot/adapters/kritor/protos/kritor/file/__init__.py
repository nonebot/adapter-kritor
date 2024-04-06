# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: file/file_data.proto, file/group_file.proto
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
class File(betterproto.Message):
    file_id: str = betterproto.string_field(1)
    file_name: str = betterproto.string_field(2)
    file_size: int = betterproto.uint64_field(3)
    bus_id: int = betterproto.int32_field(4)
    upload_time: int = betterproto.uint32_field(5)
    dead_time: int = betterproto.uint32_field(6)
    modify_time: int = betterproto.uint32_field(7)
    download_times: int = betterproto.uint32_field(8)
    uploader: int = betterproto.uint64_field(9)
    uploader_name: str = betterproto.string_field(10)
    sha: str = betterproto.string_field(11)
    sha3: str = betterproto.string_field(12)
    md5: str = betterproto.string_field(13)


@dataclass(eq=False, repr=False)
class Folder(betterproto.Message):
    folder_id: str = betterproto.string_field(1)
    folder_name: str = betterproto.string_field(2)
    total_file_count: int = betterproto.uint32_field(3)
    create_time: int = betterproto.uint32_field(4)
    creator: int = betterproto.uint64_field(5)
    creator_name: str = betterproto.string_field(6)


@dataclass(eq=False, repr=False)
class CreateFolderRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    name: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class CreateFolderResponse(betterproto.Message):
    id: str = betterproto.string_field(1)
    used_space: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class RenameFolderRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    folder_id: str = betterproto.string_field(2)
    name: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class RenameFolderResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class DeleteFolderRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    folder_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class DeleteFolderResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class UploadFileRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    file: bytes = betterproto.bytes_field(2, group="data")
    file_name: str = betterproto.string_field(3, group="data")
    file_path: str = betterproto.string_field(4, group="data")
    file_url: str = betterproto.string_field(5, group="data")


@dataclass(eq=False, repr=False)
class UploadFileResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class DeleteFileRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    file_id: str = betterproto.string_field(2)
    bus_id: int = betterproto.int32_field(3)


@dataclass(eq=False, repr=False)
class DeleteFileResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class GetFileSystemInfoRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)


@dataclass(eq=False, repr=False)
class GetFileSystemInfoResponse(betterproto.Message):
    file_count: int = betterproto.uint32_field(1)
    total_count: int = betterproto.uint32_field(2)
    used_space: int = betterproto.uint32_field(3)
    total_space: int = betterproto.uint32_field(4)


@dataclass(eq=False, repr=False)
class GetFileListRequest(betterproto.Message):
    group_id: int = betterproto.uint64_field(1)
    folder_id: Optional[str] = betterproto.string_field(2, optional=True, group="_folder_id")


@dataclass(eq=False, repr=False)
class GetFileListResponse(betterproto.Message):
    files: List["File"] = betterproto.message_field(1)
    folders: List["Folder"] = betterproto.message_field(2)


class GroupFileServiceStub(betterproto.ServiceStub):
    async def create_folder(
        self,
        create_folder_request: "CreateFolderRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "CreateFolderResponse":
        return await self._unary_unary(
            "/kritor.file.GroupFileService/CreateFolder",
            create_folder_request,
            CreateFolderResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def rename_folder(
        self,
        rename_folder_request: "RenameFolderRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "RenameFolderResponse":
        return await self._unary_unary(
            "/kritor.file.GroupFileService/RenameFolder",
            rename_folder_request,
            RenameFolderResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def delete_folder(
        self,
        delete_folder_request: "DeleteFolderRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "DeleteFolderResponse":
        return await self._unary_unary(
            "/kritor.file.GroupFileService/DeleteFolder",
            delete_folder_request,
            DeleteFolderResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def upload_file(
        self,
        upload_file_request: "UploadFileRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "UploadFileResponse":
        return await self._unary_unary(
            "/kritor.file.GroupFileService/UploadFile",
            upload_file_request,
            UploadFileResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def delete_file(
        self,
        delete_file_request: "DeleteFileRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "DeleteFileResponse":
        return await self._unary_unary(
            "/kritor.file.GroupFileService/DeleteFile",
            delete_file_request,
            DeleteFileResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_file_system_info(
        self,
        get_file_system_info_request: "GetFileSystemInfoRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GetFileSystemInfoResponse":
        return await self._unary_unary(
            "/kritor.file.GroupFileService/GetFileSystemInfo",
            get_file_system_info_request,
            GetFileSystemInfoResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_file_list(
        self,
        get_file_list_request: "GetFileListRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GetFileListResponse":
        return await self._unary_unary(
            "/kritor.file.GroupFileService/GetFileList",
            get_file_list_request,
            GetFileListResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class GroupFileServiceBase(ServiceBase):

    async def create_folder(self, create_folder_request: "CreateFolderRequest") -> "CreateFolderResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def rename_folder(self, rename_folder_request: "RenameFolderRequest") -> "RenameFolderResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def delete_folder(self, delete_folder_request: "DeleteFolderRequest") -> "DeleteFolderResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def upload_file(self, upload_file_request: "UploadFileRequest") -> "UploadFileResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def delete_file(self, delete_file_request: "DeleteFileRequest") -> "DeleteFileResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_file_system_info(
        self, get_file_system_info_request: "GetFileSystemInfoRequest"
    ) -> "GetFileSystemInfoResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_file_list(self, get_file_list_request: "GetFileListRequest") -> "GetFileListResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_create_folder(
        self, stream: "grpclib.server.Stream[CreateFolderRequest, CreateFolderResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.create_folder(request)
        await stream.send_message(response)

    async def __rpc_rename_folder(
        self, stream: "grpclib.server.Stream[RenameFolderRequest, RenameFolderResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.rename_folder(request)
        await stream.send_message(response)

    async def __rpc_delete_folder(
        self, stream: "grpclib.server.Stream[DeleteFolderRequest, DeleteFolderResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.delete_folder(request)
        await stream.send_message(response)

    async def __rpc_upload_file(self, stream: "grpclib.server.Stream[UploadFileRequest, UploadFileResponse]") -> None:
        request = await stream.recv_message()
        response = await self.upload_file(request)
        await stream.send_message(response)

    async def __rpc_delete_file(self, stream: "grpclib.server.Stream[DeleteFileRequest, DeleteFileResponse]") -> None:
        request = await stream.recv_message()
        response = await self.delete_file(request)
        await stream.send_message(response)

    async def __rpc_get_file_system_info(
        self,
        stream: "grpclib.server.Stream[GetFileSystemInfoRequest, GetFileSystemInfoResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_file_system_info(request)
        await stream.send_message(response)

    async def __rpc_get_file_list(
        self, stream: "grpclib.server.Stream[GetFileListRequest, GetFileListResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_file_list(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/kritor.file.GroupFileService/CreateFolder": grpclib.const.Handler(
                self.__rpc_create_folder,
                grpclib.const.Cardinality.UNARY_UNARY,
                CreateFolderRequest,
                CreateFolderResponse,
            ),
            "/kritor.file.GroupFileService/RenameFolder": grpclib.const.Handler(
                self.__rpc_rename_folder,
                grpclib.const.Cardinality.UNARY_UNARY,
                RenameFolderRequest,
                RenameFolderResponse,
            ),
            "/kritor.file.GroupFileService/DeleteFolder": grpclib.const.Handler(
                self.__rpc_delete_folder,
                grpclib.const.Cardinality.UNARY_UNARY,
                DeleteFolderRequest,
                DeleteFolderResponse,
            ),
            "/kritor.file.GroupFileService/UploadFile": grpclib.const.Handler(
                self.__rpc_upload_file,
                grpclib.const.Cardinality.UNARY_UNARY,
                UploadFileRequest,
                UploadFileResponse,
            ),
            "/kritor.file.GroupFileService/DeleteFile": grpclib.const.Handler(
                self.__rpc_delete_file,
                grpclib.const.Cardinality.UNARY_UNARY,
                DeleteFileRequest,
                DeleteFileResponse,
            ),
            "/kritor.file.GroupFileService/GetFileSystemInfo": grpclib.const.Handler(
                self.__rpc_get_file_system_info,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetFileSystemInfoRequest,
                GetFileSystemInfoResponse,
            ),
            "/kritor.file.GroupFileService/GetFileList": grpclib.const.Handler(
                self.__rpc_get_file_list,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetFileListRequest,
                GetFileListResponse,
            ),
        }
