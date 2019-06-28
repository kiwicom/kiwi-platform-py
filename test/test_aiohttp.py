import time
from datetime import datetime

import aiohttp
import pytest
from aiohttp import web
from freezegun import freeze_time

from kw.platform import aiohttp as uut


URL = "http://kiwi.com"


@pytest.fixture
def patch_aiohttp(mocker, app_env_vars):
    mocker.spy(aiohttp.ClientSession, "_request")

    uut.monkey.patch()

    yield

    del aiohttp.__kiwi_platform_patch  # pylint: disable=no-member


def create_app(sleep_seconds=0, middlewares=None):
    def hello(request):
        if sleep_seconds:
            time.sleep(sleep_seconds)
        return aiohttp.web.Response(text="Hello, world!")

    app = aiohttp.web.Application(middlewares=middlewares)
    app.router.add_get("/", hello)
    return app


@pytest.mark.parametrize(
    "user_agent,expected_status,current_time",
    [
        ("invalid", 200, "2019-05-21"),
        ("invalid", 400, "2020-01-01"),
        ("mambo/1a (Kiwi.com dev)", 200, "2020-01-01"),
    ],
)
async def test_user_agent_middleware__restrict(
    aiohttp_client, loop, user_agent, expected_status, current_time
):
    app = create_app(middlewares=[uut.user_agent_middleware])
    client = await aiohttp_client(app)

    with freeze_time(current_time, tick=True):
        res = await client.get("/", headers={"User-Agent": user_agent})

    assert res.status == expected_status


@pytest.mark.parametrize(
    "user_agent,sleep_seconds,expected_time,current_time",
    [
        ("invalid", 0.1, 0.2, "2019-07-26"),
        ("mambo/1a (Kiwi.com dev)", 0.1, 0.1, "2019-07-26"),
        ("invalid", 0.1, 0.1, "2019-05-07"),
    ],
)
async def test_user_agent_middleware__slowdown(
    aiohttp_client, loop, user_agent, sleep_seconds, expected_time, current_time
):
    app = create_app(sleep_seconds, middlewares=[uut.user_agent_middleware])
    client = await aiohttp_client(app)

    with freeze_time(current_time, tick=True):
        before_time = time.time()
        res = await client.get("/", headers={"User-Agent": user_agent})
        request_time = time.time() - before_time

    assert res.status == 200
    assert request_time >= expected_time


async def test_kiwi_client_session(patch_aiohttp):
    async with uut.KiwiClientSession() as client:
        async with client.get(URL) as resp:
            assert (
                resp.request_info.headers.get("User-Agent")
                == "unittest/1.0 (Kiwi.com test-env)"
            )


async def test_aiohttp_request_patched(patch_aiohttp):
    async with aiohttp.ClientSession() as client:
        async with client.get(URL) as resp:
            assert (
                resp.request_info.headers.get("User-Agent")
                == "unittest/1.0 (Kiwi.com test-env)"
            )

    assert getattr(aiohttp, "__kiwi_platform_patch") is True


async def test_aiohttp_request_not_patched():
    async with aiohttp.ClientSession() as client:
        async with client.get(URL) as resp:
            assert "aiohttp" in resp.request_info.headers.get("User-Agent")

    assert not hasattr(aiohttp, "__kiwi_platform_patch")


@pytest.mark.parametrize(
    "when, expected_sunset, info_url",
    [
        (
            datetime(2019, 8, 5, 5, 10, 0),
            "Mon, 05 Aug 2019 05:10:00 GMT",
            "https://example.com",
        ),
        (None, None, "https://example.com"),
        (datetime(2019, 8, 5, 5, 10, 0), "Mon, 05 Aug 2019 05:10:00 GMT", None),
    ],
)
async def test_aiohttp__utils_sunset(
    aiohttp_client, loop, when, expected_sunset, info_url
):
    @uut.utils.sunset(when=when, info_url=info_url)
    async def index(request):
        return web.Response(text="Index")

    result = await index("request")

    if info_url:
        assert result.headers["Link"] == '<{}>;rel="sunset"'.format(info_url)
    else:
        assert "Link" not in result.headers

    if when:
        assert result.headers["Sunset"] == expected_sunset
    else:
        assert "Sunset" not in result.headers


async def test_aiohttp__utils_sunset__append_link(aiohttp_client, loop):
    @uut.utils.sunset(info_url="https://sunset.example.com")
    async def index(request):
        return web.Response(
            text="Index", headers={"Link": '<https://meta.example.com>;rel="meta"'}
        )

    result = await index("request")
    assert result.headers["Link"] == (
        '<https://meta.example.com>;rel="meta",'
        '<https://sunset.example.com>;rel="sunset"'
    )


def test_utils_sunset__error():
    with pytest.raises(TypeError):
        uut.utils.sunset()
