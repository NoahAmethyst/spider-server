import pytest

from pb import qqbot_pb2, qqbot_pb2_grpc
from service import qqbot_notify
from service.qqbot_notify import NotifyOutcome, QQBotNotifier


def test_qqbot_notify_request_has_content_field():
    request = qqbot_pb2.NotifyReq(content="爆点")

    assert request.content == "爆点"


class CapturingChannel:
    def __init__(self):
        self.calls = []

    def unary_unary(self, path, request_serializer, response_deserializer):
        self.calls.append((path, request_serializer, response_deserializer))
        return object()


def test_qqbot_notify_stub_binds_the_notify_rpc_contract():
    channel = CapturingChannel()
    qqbot_pb2_grpc.QQBotServiceStub(channel)

    assert channel.calls == [
        (
            "/proto.QQBotService/Notify",
            qqbot_pb2.NotifyReq.SerializeToString,
            qqbot_pb2.Resp.FromString,
        )
    ]


class Stub:
    def Notify(self, request, timeout):
        assert request.content == "正文"
        assert timeout == 10
        return type("Response", (), {"message": "没有可推送的订阅者"})()


def test_notifier_classifies_no_subscribers():
    notifier = QQBotNotifier("qq-bot:9090", stub_factory=lambda _address: Stub())

    assert notifier.notify("正文") is NotifyOutcome.NO_SUBSCRIBERS


def test_notifier_classifies_other_successful_responses_as_delivered():
    class DeliveredStub:
        def Notify(self, _request, timeout):
            assert timeout == 10
            return type("Response", (), {"message": "已推送"})()

    notifier = QQBotNotifier("qq-bot:9090", stub_factory=lambda _address: DeliveredStub())

    assert notifier.notify("正文") is NotifyOutcome.DELIVERED


def test_notifier_propagates_rpc_error():
    class FailingStub:
        def Notify(self, _request, timeout):
            raise RuntimeError("unavailable")

    notifier = QQBotNotifier("qq-bot:9090", stub_factory=lambda _address: FailingStub())

    with pytest.raises(RuntimeError, match="unavailable"):
        notifier.notify("正文")


def test_default_notifier_closes_channel_after_success(monkeypatch):
    class Channel:
        closed = False

        def close(self):
            self.closed = True

    class DeliveredStub:
        def __init__(self, channel):
            assert channel is default_channel

        def Notify(self, request, timeout):
            assert request.content == "正文"
            assert timeout == 10
            return type("Response", (), {"message": "已推送"})()

    default_channel = Channel()
    monkeypatch.setattr(qqbot_notify.grpc, "insecure_channel", lambda _address: default_channel)
    monkeypatch.setattr(qqbot_notify.qqbot_pb2_grpc, "QQBotServiceStub", DeliveredStub)

    assert QQBotNotifier("qq-bot:9090").notify("正文") is NotifyOutcome.DELIVERED
    assert default_channel.closed is True


def test_default_notifier_closes_channel_after_rpc_error(monkeypatch):
    class Channel:
        closed = False

        def close(self):
            self.closed = True

    class FailingStub:
        def __init__(self, channel):
            assert channel is default_channel

        def Notify(self, _request, timeout):
            assert timeout == 10
            raise RuntimeError("unavailable")

    default_channel = Channel()
    monkeypatch.setattr(qqbot_notify.grpc, "insecure_channel", lambda _address: default_channel)
    monkeypatch.setattr(qqbot_notify.qqbot_pb2_grpc, "QQBotServiceStub", FailingStub)

    with pytest.raises(RuntimeError, match="unavailable"):
        QQBotNotifier("qq-bot:9090").notify("正文")
    assert default_channel.closed is True
