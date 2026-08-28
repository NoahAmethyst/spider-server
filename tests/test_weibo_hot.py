import pytest

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
