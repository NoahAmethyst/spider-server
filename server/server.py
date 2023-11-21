import logging
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection
from pb import spider_pb2, spider_pb2_grpc
from service import bing_daily_img


class SpiderService(spider_pb2_grpc.SpiderServiceServicer):
    async def GetCNBingWallPaper(
            self,
            request: spider_pb2.SpiderReq,
            context: grpc.aio.ServicerContext,
    ) -> spider_pb2.SpiderResp:
        url, _ = bing_daily_img.get_bing_wallpaper_cn(request.is_mobile)
        return spider_pb2.SpiderResp(url=url)

    async def GetUSBingWallPaper(
            self,
            request: spider_pb2.SpiderReq,
            context: grpc.aio.ServicerContext,
    ) -> spider_pb2.SpiderResp:
        url, _ = bing_daily_img.get_bing_wallpaper_us(request.is_mobile)
        return spider_pb2.SpiderResp(url=url)


async def start(addr) -> None:
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    spider_pb2_grpc.add_SpiderServiceServicer_to_server(SpiderService(), server)
    listen_addr = "0.0.0.0:9090"
    if addr is not None:
        listen_addr = "0.0.0.0:{}".format(addr)
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)

    SERVICE_NAMES = (
        spider_pb2.DESCRIPTOR.services_by_name['SpiderService'].full_name,
        reflection.SERVICE_NAME
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    await server.start()
    await server.wait_for_termination()
