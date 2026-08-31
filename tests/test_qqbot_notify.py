from pb import qqbot_pb2, qqbot_pb2_grpc


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
