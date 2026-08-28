import pytest
import requests
import importlib
import os
import subprocess
import sys
from pathlib import Path

from pb import spider_pb2
from service import weibo_hot


WEIBO_HOT_HTML = """
<table>
  <tbody>
    <tr>
      <td class="td-01 ranktop">1</td>
      <td class="td-02"><a href="/weibo?q=%23%E6%99%AE%E9%80%9A%E7%83%AD%E6%90%9C%23">普通热搜</a><span>701234</span></td>
    </tr>
    <tr>
      <td class="td-01 ranktop">3</td>
      <td class="td-02"><a href="/u/recommendation">推荐内容</a><span>689000</span><span class="icon-txt">荐</span></td>
    </tr>
    <tr>
      <td class="td-01 ranktop">8</td>
      <td class="td-02"><a href="/weibo?q=%23%E7%88%86%E6%AC%BE%E6%96%B0%E8%AF%9D%E9%A2%98%23">爆款新话题</a><span>602000</span><span class="icon-txt">爆</span><span class="icon-txt">新</span><span class="icon-txt">未知</span></td>
    </tr>
  </tbody>
</table>
""".encode()


def test_weibo_hot_exposes_repeated_tags():
    hot = spider_pb2.WeiboHot(tags=["爆", "新"])

    assert list(hot.tags) == ["爆", "新"]


def test_server_module_imports_generated_grpc_stubs():
    assert importlib.import_module("server.server")


def test_protocol_generation_script_runs_from_project_root():
    project_root = Path(__file__).resolve().parents[1]
    environment = os.environ | {"PYTHON_BIN": sys.executable}

    result = subprocess.run(
        ["bash", "protocol/gen.sh"],
        cwd=project_root,
        env=environment,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_weibo_hot_targets_my_hot_category():
    assert weibo_hot.WEIBO_TOP_URL == "https://s.weibo.com/top/summary?cate=recommend"


def test_parser_preserves_raw_rank_heat_and_all_tags():
    rows = weibo_hot.parse_weibo_hot_html(WEIBO_HOT_HTML)

    assert [(row.rank, row.title, row.hot, list(row.tags)) for row in rows] == [
        (1, "普通热搜", 701234, []),
        (3, "推荐内容", 689000, ["荐"]),
        (8, "爆款新话题", 602000, ["爆", "新", "未知"]),
    ]
    assert rows[1].url == "https://s.weibo.com/u/recommendation"


def test_parser_rejects_visitor_html():
    with pytest.raises(ValueError, match="no ranking rows"):
        weibo_hot.parse_weibo_hot_html(b"<html><title>Sina Visitor System</title></html>")


def test_parser_preserves_unclassed_status_tags():
    html = """
    <table><tr>
      <td class="td-01">12</td>
      <td class="td-02">
        <a href="/weibo?q=%23%E7%83%AD%E6%90%9C%23">热搜词条</a>
        <span>456789</span><span>当前爆词</span><span>04:06登顶</span>
      </td>
    </tr></table>
    """.encode()

    [row] = weibo_hot.parse_weibo_hot_html(html)

    assert row.hot == 456789
    assert list(row.tags) == ["当前爆词", "04:06登顶"]


class FakeResponse:
    def __init__(self, content=WEIBO_HOT_HTML):
        self.content = content

    def raise_for_status(self):
        return None


def test_get_weibo_hot_omits_cookie_when_not_configured(monkeypatch):
    requested = {}

    def fake_get(url, **kwargs):
        requested["url"] = url
        requested.update(kwargs)
        return FakeResponse()

    monkeypatch.delenv("WEIBO_COOKIE", raising=False)
    monkeypatch.setattr(weibo_hot.requests, "get", fake_get)

    weibo_hot.get_weibo_hot()

    assert requested["url"] == weibo_hot.WEIBO_TOP_URL
    assert "Cookie" not in requested["headers"]
    assert requested["timeout"] == weibo_hot.REQUEST_TIMEOUT_SECONDS


def test_get_weibo_hot_uses_configured_cookie(monkeypatch):
    requested = {}

    def fake_get(_url, **kwargs):
        requested.update(kwargs)
        return FakeResponse()

    monkeypatch.setenv("WEIBO_COOKIE", "session=value")
    monkeypatch.setattr(weibo_hot.requests, "get", fake_get)

    weibo_hot.get_weibo_hot()

    assert requested["headers"]["Cookie"] == "session=value"


def test_get_weibo_hot_raises_http_error_for_non_success_response(monkeypatch):
    response = requests.Response()
    response.status_code = 403
    response.url = weibo_hot.WEIBO_TOP_URL
    response._content = b"forbidden"
    monkeypatch.setattr(weibo_hot.requests, "get", lambda *_args, **_kwargs: response)

    with pytest.raises(requests.HTTPError):
        weibo_hot.get_weibo_hot()
