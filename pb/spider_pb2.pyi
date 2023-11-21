from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SpiderReq(_message.Message):
    __slots__ = ["is_mobile"]
    IS_MOBILE_FIELD_NUMBER: _ClassVar[int]
    is_mobile: bool
    def __init__(self, is_mobile: bool = ...) -> None: ...

class SpiderResp(_message.Message):
    __slots__ = ["url"]
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...
