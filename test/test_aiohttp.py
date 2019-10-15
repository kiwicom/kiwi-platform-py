import time
from datetime import datetime

import aiohttp
import pytest
import wrapt
from aiohttp import web
from aioresponses import aioresponses
from freezegun import freeze_time

from kw.platform import aiohttp as uut


@pytest.fixture
def patch_aiohttp(mocker, app_env_vars):
    mocker.spy(aiohttp.ClientSession, "_request")

    uut.monkey.patch()

    yield

    del aiohttp.__kiwi_platform_patch  # pylint: disable=no-member


@pytest.fixture
def aiomock():
    with aioresponses() as m:
        yield m


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
async def test_aiohttp__user_agent_middleware__restrict(
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
async def test_aiohttp__user_agent_middleware__slowdown(
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


async def test_aiohttp__kiwi_client_session__sunset(loop, mocker, aiomock):
    m_capture_message = mocker.patch("kw.platform.utils.capture_message")
    mocker.patch("kw.platform.aiohttp.session.add_user_agent_header")

    url = "http://kiwi.com"
    sunset_date = "Sat, 31 Dec 2018 23:59:59 GMT"

    aiomock.get(url, headers={"Sunset": sunset_date})

    async with uut.KiwiClientSession() as client:
        async with client.get(url) as resp:
            await resp.text()
            assert "Sunset" in resp.headers

    m_capture_message.assert_called_once_with(
        "The Sunset header found in the HTTP response: " + sunset_date, level="warning"
    )


async def test_aiohttp__kiwi_client_session__user_agent(httpbin, app_env_vars):
    async with uut.KiwiClientSession() as client:
        async with client.get(httpbin.url) as resp:
            assert (
                resp.request_info.headers.get("User-Agent")
                == "unittest/1.0 (Kiwi.com test-env)"
            )


async def test_aiohttp__request_patched(httpbin, patch_aiohttp):
    async with aiohttp.ClientSession() as client:
        async with client.get(httpbin.url) as resp:
            assert (
                resp.request_info.headers.get("User-Agent")
                == "unittest/1.0 (Kiwi.com test-env)"
            )

    assert getattr(aiohttp, "__kiwi_platform_patch") is True


async def test_aiohttp__request_not_patched(httpbin):
    async with aiohttp.ClientSession() as client:
        async with client.get(httpbin.url) as resp:
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


def test_aiohttp__utils_sunset__error():
    with pytest.raises(TypeError):
        uut.utils.sunset()


def test_aiohttp_patched(patch_aiohttp):
    assert hasattr(aiohttp.ClientSession._request, "__wrapped__")
    assert getattr(aiohttp, "__kiwi_platform_patch") is True


def test_aiohttp_not_patched():
    assert not hasattr(aiohttp.ClientSession._request, "__wrapped__")
    assert not hasattr(aiohttp, "__kiwi_platform_patch")


@pytest.mark.parametrize(
    "sunset_date,sunset_link,expected_message",
    [
        (None, None, None),
        (
            "Sat, 31 Dec 2018 23:59:59 GMT",
            None,
            "The Sunset header found in the HTTP response: {sd}",
        ),
        (
            None,
            "http://kiwi.com/sunset",
            "The Sunset Link relation type found in the HTTP response: {sl}",
        ),
        (
            "Sat, 31 Dec 2018 23:59:59 GMT",
            "http://kiwi.com/sunset",
            "The Sunset header found in the HTTP response: {sd}, additional info: {sl}",
        ),
    ],
)
async def test_aiohttp__patch_with_sentry__sunset(
    loop, aiomock, mocker, sunset_date, sunset_link, expected_message
):
    m_capture_message = mocker.patch("kw.platform.utils.capture_message")

    url = "http://kiwi.com"

    headers = {}
    if sunset_date:
        headers["Sunset"] = sunset_date
    if sunset_link:
        headers["Link"] = '<{}>;rel="sunset"'.format(sunset_link)

    aiomock.get(url, headers=headers)

    async with aiohttp.ClientSession() as client:
        async with client.get(url) as resp:
            await resp.text()

    m_capture_message.assert_not_called()

    aiomock.get(url, headers=headers)

    async with aiohttp.ClientSession() as client:
        wrapt.wrap_function_wrapper(
            client, "_request", uut.monkey._add_sentry_handler()
        )
        async with client.get(url) as resp:
            await resp.text()

    if expected_message:
        m_capture_message.assert_called_once_with(
            expected_message.format(sd=sunset_date, sl=sunset_link), level="warning"
        )
    else:
        m_capture_message.assert_not_called()


@pytest.mark.parametrize("message", ["Will be deprecated soon", None])
async def test_aiohttp__patch_with_sentry__deprecated_usage(
    loop, aiomock, mocker, message
):
    m_capture_message = mocker.patch("kw.platform.utils.capture_message")

    url = "http://kiwi.com"

    headers = {}
    if message:
        headers["Deprecated-Usage"] = message

    aiomock.get(url, headers=headers)

    async with aiohttp.ClientSession() as client:
        async with client.get(url) as resp:
            await resp.text()

    m_capture_message.assert_not_called()

    aiomock.get(url, headers=headers)

    async with aiohttp.ClientSession() as client:
        wrapt.wrap_function_wrapper(
            client, "_request", uut.monkey._add_sentry_handler()
        )
        async with client.get(url) as resp:
            await resp.text()

    if message:
        m_capture_message.assert_called_once_with(message, level="warning")
    else:
        m_capture_message.assert_not_called()
