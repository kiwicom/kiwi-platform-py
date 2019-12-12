import time

import pytest
from freezegun import freeze_time
from webob.request import BaseRequest

from kw.platform import wsgi as uut


def create_app(sleep_seconds=0):
    def simple_app(environ, start_response):
        if sleep_seconds:
            time.sleep(sleep_seconds)
        start_response("200 OK", [("Content-Type", "text/html; charset=UTF-8")])
        return ["OK"]

    return simple_app


@pytest.mark.parametrize(
    "user_agent,expected_status,current_time",
    [
        ("invalid", 200, "2019-05-21"),
        (None, 400, "2020-01-01"),
        ("", 400, "2020-01-01"),
        ("invalid", 400, "2020-01-01"),
        ("mambo/1a (Kiwi.com dev)", 200, "2020-01-01"),
    ],
)
def test_user_agent_middleware__restrict(user_agent, expected_status, current_time):
    app = create_app()

    req = BaseRequest.blank("/")
    if user_agent is not None:
        req.user_agent = user_agent

    with freeze_time(current_time, tick=True):
        app = uut.user_agent_middleware(app)
        res = req.get_response(app)

    assert res.status_code == expected_status


@pytest.mark.parametrize(
    "user_agent,sleep_seconds,expected_time,current_time",
    [
        (None, 0.1, 0.2, "2019-07-26"),
        ("", 0.1, 0.2, "2019-07-26"),
        ("invalid", 0.1, 0.2, "2019-07-26"),
        ("mambo/1a (Kiwi.com dev)", 0.1, 0.1, "2019-07-26"),
        ("invalid", 0.1, 0.1, "2019-05-07"),
    ],
)
def test_user_agent_middleware__slowdown(
    user_agent, sleep_seconds, expected_time, current_time
):
    app = create_app(sleep_seconds=sleep_seconds)

    req = BaseRequest.blank("/")
    if user_agent is not None:
        req.user_agent = user_agent

    with freeze_time(current_time, tick=True):
        app = uut.user_agent_middleware(app)

        before_time = time.time()
        res = req.get_response(app)
        request_time = time.time() - before_time

    assert res.status_code == 200
    assert request_time >= expected_time
