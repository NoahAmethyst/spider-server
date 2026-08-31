from pb import qqbot_pb2


def test_qqbot_notify_request_has_content_field():
    request = qqbot_pb2.NotifyReq(content="爆点")

    assert request.content == "爆点"
