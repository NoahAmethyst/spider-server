import json

import pytest
import requests

from service import bing_daily_img


def _response(status_code, body):
    response = requests.Response()
    response.status_code = status_code
    response.url = "https://example.test/HPImageArchive.aspx"
    if isinstance(body, dict):
        response._content = json.dumps(body).encode()
        response.headers["content-type"] = "application/json"
    else:
        response._content = body.encode()
        response.headers["content-type"] = "text/plain"
    return response


def _disable_retry_delay_and_logs(monkeypatch):
    monkeypatch.setattr(bing_daily_img.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(bing_daily_img.logger, "disabled", True)
    bing_daily_img.cache.clear()


def test_us_wallpaper_falls_back_to_bing_after_configured_host_fails(monkeypatch):
    _disable_retry_delay_and_logs(monkeypatch)
    monkeypatch.setenv("REMOTE_HOST", "retired-proxy.example")
    responses = [
        _response(404, "deployment not found"),
        _response(
            200,
            {
                "images": [
                    {
                        "url": "/th?id=OHR.Test_EN-US.jpg",
                        "urlbase": "/th?id=OHR.Test_EN-US",
                    }
                ]
            },
        ),
    ]
    requested_urls = []

    def fake_get(url, **_kwargs):
        requested_urls.append(url)
        return responses.pop(0)

    monkeypatch.setattr(bing_daily_img.requests, "get", fake_get)

    image_url, image_id = bing_daily_img.get_bing_wallpaper_us(is_mobile=True)

    assert requested_urls == [
        "https://retired-proxy.example/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US",
        "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US",
    ]
    assert image_url == "http://www.bing.com/th?id=OHR.Test_EN-US_1080x1920.jpg"
    assert image_id == "Test"


def test_us_wallpaper_stops_after_three_failed_requests(monkeypatch):
    _disable_retry_delay_and_logs(monkeypatch)
    monkeypatch.setenv("REMOTE_HOST", "retired-proxy.example")
    requested_urls = []

    def fake_get(url, **_kwargs):
        requested_urls.append(url)
        return _response(404, "deployment not found")

    monkeypatch.setattr(bing_daily_img.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        bing_daily_img.get_bing_wallpaper_us(is_mobile=False)

    assert requested_urls == [
        "https://retired-proxy.example/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US",
        "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US",
        "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US",
    ]
