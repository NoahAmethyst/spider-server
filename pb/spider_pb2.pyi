from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SpiderReq(_message.Message):
    __slots__ = ["is_mobile", "size", "prompt"]
    IS_MOBILE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    is_mobile: bool
    size: int
    prompt: str
    def __init__(self, is_mobile: bool = ..., size: _Optional[int] = ..., prompt: _Optional[str] = ...) -> None: ...

class SpiderResp(_message.Message):
    __slots__ = ["url", "error", "weiboHotList", "d36KrHotList", "wallStreetNews", "zhihuHotList", "odailyFeeds", "caiXinNews", "copilotResp"]
    URL_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    WEIBOHOTLIST_FIELD_NUMBER: _ClassVar[int]
    D36KRHOTLIST_FIELD_NUMBER: _ClassVar[int]
    WALLSTREETNEWS_FIELD_NUMBER: _ClassVar[int]
    ZHIHUHOTLIST_FIELD_NUMBER: _ClassVar[int]
    ODAILYFEEDS_FIELD_NUMBER: _ClassVar[int]
    CAIXINNEWS_FIELD_NUMBER: _ClassVar[int]
    COPILOTRESP_FIELD_NUMBER: _ClassVar[int]
    url: str
    error: str
    weiboHotList: _containers.RepeatedCompositeFieldContainer[WeiboHot]
    d36KrHotList: _containers.RepeatedCompositeFieldContainer[D36KrHot]
    wallStreetNews: _containers.RepeatedCompositeFieldContainer[WallStreetNew]
    zhihuHotList: _containers.RepeatedCompositeFieldContainer[ZhihuHot]
    odailyFeeds: _containers.RepeatedCompositeFieldContainer[OdailyFeed]
    caiXinNews: _containers.RepeatedCompositeFieldContainer[CaiXinNew]
    copilotResp: CopilotResp
    def __init__(self, url: _Optional[str] = ..., error: _Optional[str] = ..., weiboHotList: _Optional[_Iterable[_Union[WeiboHot, _Mapping]]] = ..., d36KrHotList: _Optional[_Iterable[_Union[D36KrHot, _Mapping]]] = ..., wallStreetNews: _Optional[_Iterable[_Union[WallStreetNew, _Mapping]]] = ..., zhihuHotList: _Optional[_Iterable[_Union[ZhihuHot, _Mapping]]] = ..., odailyFeeds: _Optional[_Iterable[_Union[OdailyFeed, _Mapping]]] = ..., caiXinNews: _Optional[_Iterable[_Union[CaiXinNew, _Mapping]]] = ..., copilotResp: _Optional[_Union[CopilotResp, _Mapping]] = ...) -> None: ...

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

class OdailyFeed(_message.Message):
    __slots__ = ["title", "reference_url", "id", "description", "url", "published_at"]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_URL_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_AT_FIELD_NUMBER: _ClassVar[int]
    title: str
    reference_url: str
    id: int
    description: str
    url: str
    published_at: int
    def __init__(self, title: _Optional[str] = ..., reference_url: _Optional[str] = ..., id: _Optional[int] = ..., description: _Optional[str] = ..., url: _Optional[str] = ..., published_at: _Optional[int] = ...) -> None: ...

class CopilotResp(_message.Message):
    __slots__ = ["content", "suggestions"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    content: str
    suggestions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, content: _Optional[str] = ..., suggestions: _Optional[_Iterable[str]] = ...) -> None: ...

class CaiXinNew(_message.Message):
    __slots__ = ["title", "description", "url", "domain"]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    url: str
    domain: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., url: _Optional[str] = ..., domain: _Optional[str] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ["title", "resource", "content", "reference_url", "img_urls", "references"]
    class ReferencesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TITLE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_URL_FIELD_NUMBER: _ClassVar[int]
    IMG_URLS_FIELD_NUMBER: _ClassVar[int]
    REFERENCES_FIELD_NUMBER: _ClassVar[int]
    title: str
    resource: str
    content: str
    reference_url: str
    img_urls: _containers.RepeatedScalarFieldContainer[str]
    references: _containers.ScalarMap[str, str]
    def __init__(self, title: _Optional[str] = ..., resource: _Optional[str] = ..., content: _Optional[str] = ..., reference_url: _Optional[str] = ..., img_urls: _Optional[_Iterable[str]] = ..., references: _Optional[_Mapping[str, str]] = ...) -> None: ...
