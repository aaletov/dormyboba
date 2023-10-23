from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ADMIN_ROLE: _ClassVar[Role]
    CLIENT_ROLE: _ClassVar[Role]

class Platform(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VK: _ClassVar[Platform]
ADMIN_ROLE: Role
CLIENT_ROLE: Role
VK: Platform

class ClientId(_message.Message):
    __slots__ = ["platform", "id"]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    platform: Platform
    id: str
    def __init__(self, platform: _Optional[_Union[Platform, str]] = ..., id: _Optional[str] = ...) -> None: ...

class GetRoleRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: ClientId
    def __init__(self, id: _Optional[_Union[ClientId, _Mapping]] = ...) -> None: ...

class GetRoleResponse(_message.Message):
    __slots__ = ["role"]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: Role
    def __init__(self, role: _Optional[_Union[Role, str]] = ...) -> None: ...
