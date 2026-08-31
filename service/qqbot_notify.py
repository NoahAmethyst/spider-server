from enum import Enum

import grpc

from pb import qqbot_pb2, qqbot_pb2_grpc


class NotifyOutcome(Enum):
    DELIVERED = "delivered"
    NO_SUBSCRIBERS = "no_subscribers"


class QQBotNotifier:
    def __init__(self, address: str, stub_factory=None):
        self._address = address
        self._stub_factory = stub_factory

    def notify(self, content: str) -> NotifyOutcome:
        request = qqbot_pb2.NotifyReq(content=content)
        if self._stub_factory is not None:
            response = self._stub_factory(self._address).Notify(request, timeout=10)
        else:
            channel = grpc.insecure_channel(self._address)
            try:
                stub = qqbot_pb2_grpc.QQBotServiceStub(channel)
                response = stub.Notify(request, timeout=10)
            finally:
                channel.close()

        if response.message == "没有可推送的订阅者":
            return NotifyOutcome.NO_SUBSCRIBERS
        return NotifyOutcome.DELIVERED
