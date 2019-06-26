import time

import pytest
from aiohttp import web
from freezegun import freeze_time

from kw.platform import aiohttp as uut


def create_app(sleep_seconds=0, middlewares=None):
    def hello(request):
        if sleep_seconds:
            time.sleep(sleep_seconds)
        return web.Response(text="Hello, world!")

    app = web.Application(middlewares=middlewares)
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
