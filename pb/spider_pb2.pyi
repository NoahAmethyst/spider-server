from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FinanceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[FinanceType]
    GOLD: _ClassVar[FinanceType]
    EXCHANGE: _ClassVar[FinanceType]
    CURRENCY_LIST: _ClassVar[FinanceType]
UNKNOWN: FinanceType
GOLD: FinanceType
EXCHANGE: FinanceType
CURRENCY_LIST: FinanceType

class SpiderReq(_message.Message):
    __slots__ = ["is_mobile", "size", "prompt", "finance_type", "_from", "_to"]
    IS_MOBILE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    FINANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    _FROM_FIELD_NUMBER: _ClassVar[int]
    _TO_FIELD_NUMBER: _ClassVar[int]
    is_mobile: bool
    size: int
    prompt: str
    finance_type: FinanceType
    _from: str
    _to: str
    def __init__(self, is_mobile: bool = ..., size: _Optional[int] = ..., prompt: _Optional[str] = ..., finance_type: _Optional[_Union[FinanceType, str]] = ..., _from: _Optional[str] = ..., _to: _Optional[str] = ...) -> None: ...

class SpiderResp(_message.Message):
    __slots__ = ["url", "error", "weiboHotList", "d36KrHotList", "wallStreetNews", "zhihuHotList", "odailyFeeds", "copilotResp", "caiXinNews", "finance_resp"]
    URL_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    WEIBOHOTLIST_FIELD_NUMBER: _ClassVar[int]
    D36KRHOTLIST_FIELD_NUMBER: _ClassVar[int]
    WALLSTREETNEWS_FIELD_NUMBER: _ClassVar[int]
    ZHIHUHOTLIST_FIELD_NUMBER: _ClassVar[int]
    ODAILYFEEDS_FIELD_NUMBER: _ClassVar[int]
    COPILOTRESP_FIELD_NUMBER: _ClassVar[int]
    CAIXINNEWS_FIELD_NUMBER: _ClassVar[int]
    FINANCE_RESP_FIELD_NUMBER: _ClassVar[int]
    url: str
    error: str
    weiboHotList: _containers.RepeatedCompositeFieldContainer[WeiboHot]
    d36KrHotList: _containers.RepeatedCompositeFieldContainer[D36KrHot]
    wallStreetNews: _containers.RepeatedCompositeFieldContainer[WallStreetNew]
    zhihuHotList: _containers.RepeatedCompositeFieldContainer[ZhihuHot]
    odailyFeeds: _containers.RepeatedCompositeFieldContainer[OdailyFeed]
    copilotResp: CopilotResp
    caiXinNews: _containers.RepeatedCompositeFieldContainer[CaiXinNew]
    finance_resp: FinanceResp
    def __init__(self, url: _Optional[str] = ..., error: _Optional[str] = ..., weiboHotList: _Optional[_Iterable[_Union[WeiboHot, _Mapping]]] = ..., d36KrHotList: _Optional[_Iterable[_Union[D36KrHot, _Mapping]]] = ..., wallStreetNews: _Optional[_Iterable[_Union[WallStreetNew, _Mapping]]] = ..., zhihuHotList: _Optional[_Iterable[_Union[ZhihuHot, _Mapping]]] = ..., odailyFeeds: _Optional[_Iterable[_Union[OdailyFeed, _Mapping]]] = ..., copilotResp: _Optional[_Union[CopilotResp, _Mapping]] = ..., caiXinNews: _Optional[_Iterable[_Union[CaiXinNew, _Mapping]]] = ..., finance_resp: _Optional[_Union[FinanceResp, _Mapping]] = ...) -> None: ...

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

class FinanceResp(_message.Message):
    __slots__ = ["float_value", "str_list"]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    STR_LIST_FIELD_NUMBER: _ClassVar[int]
    float_value: float
    str_list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, float_value: _Optional[float] = ..., str_list: _Optional[_Iterable[str]] = ...) -> None: ...
