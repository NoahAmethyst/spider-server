# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from pb import spider_pb2 as spider__pb2


class SpiderServiceStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetCNBingWallPaper = channel.unary_unary(
                '/proto.SpiderService/GetCNBingWallPaper',
                request_serializer=spider__pb2.Empty.SerializeToString,
                response_deserializer=spider__pb2.SpiderResp.FromString,
                )
        self.GetUSBingWallPaper = channel.unary_unary(
                '/proto.SpiderService/GetUSBingWallPaper',
                request_serializer=spider__pb2.Empty.SerializeToString,
                response_deserializer=spider__pb2.SpiderResp.FromString,
                )


class SpiderServiceServicer(object):
    """The greeting service definition.
    """

    def GetCNBingWallPaper(self, request, context):
        """Sends a greeting
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUSBingWallPaper(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SpiderServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetCNBingWallPaper': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCNBingWallPaper,
                    request_deserializer=spider__pb2.Empty.FromString,
                    response_serializer=spider__pb2.SpiderResp.SerializeToString,
            ),
            'GetUSBingWallPaper': grpc.unary_unary_rpc_method_handler(
                    servicer.GetUSBingWallPaper,
                    request_deserializer=spider__pb2.Empty.FromString,
                    response_serializer=spider__pb2.SpiderResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'proto.SpiderService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SpiderService(object):
    """The greeting service definition.
    """

    @staticmethod
    def GetCNBingWallPaper(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/proto.SpiderService/GetCNBingWallPaper',
            spider__pb2.Empty.SerializeToString,
            spider__pb2.SpiderResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetUSBingWallPaper(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/proto.SpiderService/GetUSBingWallPaper',
            spider__pb2.Empty.SerializeToString,
            spider__pb2.SpiderResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
