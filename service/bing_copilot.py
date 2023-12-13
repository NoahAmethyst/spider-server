from sydney import SydneyClient

from pb.spider_pb2 import CopilotResp


async def ask_copilot(prompt):
    async with SydneyClient() as sydney:
        sydney.use_proxy = True
        response = await sydney.ask(prompt, citations=False, suggestions=True)
        data = CopilotResp()
        data.content = response[0]
        for suggestion in response[1]:
            data.suggestions.extend(suggestion.__str__())
        return data
