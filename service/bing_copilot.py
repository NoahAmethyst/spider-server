import json
import os

import requests
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


def ask_copilot_http(prompt):
    url = os.environ.get('BING_COPILOT_SERVER')
    headers = {'Content-Type': 'application/json'}

    _data = {'message': prompt}
    response = requests.post(url, headers=headers, data=json.dumps(_data), verify=False)
    resp_json = response.json()
    data = CopilotResp()
    data.content = resp_json['content']

    data.suggestions.extend(resp_json['suggestions'])
    return data
