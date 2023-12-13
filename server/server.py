import logging
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection
from pb import spider_pb2, spider_pb2_grpc
from service import bing_daily_img
from service.bing_copilot import ask_copilot
from service.d36kr import get_36kr_hot
from service.wallstreeet_news import get_wallstreet_news
from service.weibo_hot import get_weibo_hot
from service.zhihu_hot import get_zhihu_hot
from util.logger import logger


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

    async def WeiboHot(
            self,
            request: spider_pb2.SpiderReq,
            context: grpc.aio.ServicerContext,
    ) -> spider_pb2.SpiderResp:
        resp = spider_pb2.SpiderResp()
        try:
            data = get_weibo_hot()
            if request.size > 0:
                resp.weiboHotList.extend(data[:request.size])
            else:
                resp.weiboHotList.extend(data)
        except Exception as e:
            logger.error(e)
            resp.error = e.__str__()

        return resp

    async def D36KrHot(
            self,
            request: spider_pb2.SpiderReq,
            context: grpc.aio.ServicerContext,
    ) -> spider_pb2.SpiderResp:
        resp = spider_pb2.SpiderResp()
        try:
            data = get_36kr_hot()
            if request.size > 0:
                resp.d36KrHotList.extend(data[:request.size])
            else:
                resp.d36KrHotList.extend(data)
        except Exception as e:
            logger.error(e)
            resp.error = e.__str__()

        return resp

    async def WallStreetNews(
            self,
            request: spider_pb2.SpiderReq,
            context: grpc.aio.ServicerContext,
    ) -> spider_pb2.SpiderResp:
        resp = spider_pb2.SpiderResp()
        try:
            data = get_wallstreet_news()
            if request.size > 0:
                resp.wallStreetNews.extend(data[:request.size])
            else:
                resp.wallStreetNews.extend(data)
        except Exception as e:
            logger.error(e)
            resp.error = e.__str__()

        return resp

    async def ZhihuHot(
            self,
            request: spider_pb2.SpiderReq,
            context: grpc.aio.ServicerContext,
    ) -> spider_pb2.SpiderResp:
        resp = spider_pb2.SpiderResp()
        try:
            data = get_zhihu_hot()
            if request.size > 0:
                resp.zhihuHotList.extend(data[:request.size])
            else:
                resp.zhihuHotList.extend(data)
        except Exception as e:
            logger.error(e)
            resp.error = e.__str__()

        return resp

    async def AskCopilot(
            self,
            request: spider_pb2.SpiderReq,
            context: grpc.aio.ServicerContext,
    ) -> spider_pb2.SpiderResp:
        resp = spider_pb2.SpiderResp()
        try:
            data = await ask_copilot(request.prompt)
            resp.copilotResp.CopyFrom(data)
        except Exception as e:
            logger.error(e)
            resp.error = e.__str__()
        return resp


async def start(addr) -> None:
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    spider_pb2_grpc.add_SpiderServiceServicer_to_server(SpiderService(), server)
    listen_addr = "0.0.0.0:9090"
    if addr is not None:
        listen_addr = "0.0.0.0:{}".format(addr)
    server.add_insecure_port(listen_addr)
    logger.info("Starting server on %s", listen_addr)

    SERVICE_NAMES = (
        spider_pb2.DESCRIPTOR.services_by_name['SpiderService'].full_name,
        reflection.SERVICE_NAME
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    await server.start()
    await server.wait_for_termination()
