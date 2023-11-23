from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SpiderReq(_message.Message):
    __slots__ = ["is_mobile", "size"]
    IS_MOBILE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    is_mobile: bool
    size: int
    def __init__(self, is_mobile: bool = ..., size: _Optional[int] = ...) -> None: ...

class SpiderResp(_message.Message):
    __slots__ = ["url", "error", "weiboHotList", "d36KrHotList", "wallStreetNews", "zhihuHotList"]
    URL_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    WEIBOHOTLIST_FIELD_NUMBER: _ClassVar[int]
    D36KRHOTLIST_FIELD_NUMBER: _ClassVar[int]
    WALLSTREETNEWS_FIELD_NUMBER: _ClassVar[int]
    ZHIHUHOTLIST_FIELD_NUMBER: _ClassVar[int]
    url: str
    error: str
    weiboHotList: _containers.RepeatedCompositeFieldContainer[WeiboHot]
    d36KrHotList: _containers.RepeatedCompositeFieldContainer[D36KrHot]
    wallStreetNews: _containers.RepeatedCompositeFieldContainer[WallStreetNew]
    zhihuHotList: _containers.RepeatedCompositeFieldContainer[ZhihuHot]
    def __init__(self, url: _Optional[str] = ..., error: _Optional[str] = ..., weiboHotList: _Optional[_Iterable[_Union[WeiboHot, _Mapping]]] = ..., d36KrHotList: _Optional[_Iterable[_Union[D36KrHot, _Mapping]]] = ..., wallStreetNews: _Optional[_Iterable[_Union[WallStreetNew, _Mapping]]] = ..., zhihuHotList: _Optional[_Iterable[_Union[ZhihuHot, _Mapping]]] = ...) -> None: ...

class WeiboHot(_message.Message):
    __slots__ = ["title", "url", "hot", "rank"]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    HOT_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    title: str
    url: str
    hot: int
    rank: int
    def __init__(self, title: _Optional[str] = ..., url: _Optional[str] = ..., hot: _Optional[int] = ..., rank: _Optional[int] = ...) -> None: ...

class D36KrHot(_message.Message):
    __slots__ = ["title", "url", "rank"]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    title: str
    url: str
    rank: int
    def __init__(self, title: _Optional[str] = ..., url: _Optional[str] = ..., rank: _Optional[int] = ...) -> None: ...

class WallStreetNew(_message.Message):
    __slots__ = ["title", "url", "content"]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    title: str
    url: str
    content: str
    def __init__(self, title: _Optional[str] = ..., url: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ZhihuHot(_message.Message):
    __slots__ = ["title", "url", "excerpt", "rank", "created"]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    EXCERPT_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    title: str
    url: str
    excerpt: str
    rank: int
    created: int
    def __init__(self, title: _Optional[str] = ..., url: _Optional[str] = ..., excerpt: _Optional[str] = ..., rank: _Optional[int] = ..., created: _Optional[int] = ...) -> None: ...
