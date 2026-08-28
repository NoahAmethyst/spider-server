from pb import spider_pb2


def test_weibo_hot_exposes_repeated_tags():
    hot = spider_pb2.WeiboHot(tags=["爆", "新"])

    assert list(hot.tags) == ["爆", "新"]
