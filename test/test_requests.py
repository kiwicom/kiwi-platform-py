import httpretty
import pytest
import requests
import wrapt

from kw.platform import requests as uut
from kw.platform import wrappers


URL = "http://kiwi.com"


@pytest.fixture
def patch_requests(mocker, app_env_vars):
    mocker.spy(requests.Session, "request")

    uut.monkey.patch()

    yield

    del requests.__kiwi_platform_patch  # pylint: disable=no-member


@pytest.fixture
def http():
    httpretty.enable()
    try:
        yield httpretty
    finally:
        httpretty.disable()
        httpretty.reset()


def test_requests__kiwi_session(http, mocker, app_env_vars):
    m_capture_message = mocker.patch("kw.platform.utils.capture_message")

    sunset_date = "Sat, 31 Dec 2018 23:59:59 GMT"

    http.register_uri(
        http.GET, URL, body="Hello", adding_headers={"Sunset": sunset_date}
    )

    resp = uut.KiwiSession().get(URL)

    assert resp.request.headers["User-Agent"] == "unittest/1.0 (Kiwi.com test-env)"
    m_capture_message.assert_called_once_with(
        "The Sunset header found in the HTTP response: " + sunset_date, level="warning"
    )


def test_requests__patched(http, patch_requests):
    http.register_uri(http.GET, URL, body="Kiwi.com frontpage")

    res = requests.get(URL)

    assert res.request.headers["User-Agent"] == "unittest/1.0 (Kiwi.com test-env)"
    assert getattr(requests, "__kiwi_platform_patch") is True


def test_requests__not_patched(http):
    http.register_uri(http.GET, URL, body="Kiwi.com frontpage")

    res = requests.get(URL)

    assert "requests" in res.request.headers["User-Agent"]
    assert not hasattr(requests, "__kiwi_platform_patch")


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
def test_requests__patch_with_sentry__sunset(
    http, mocker, sunset_date, sunset_link, expected_message
):
    m_capture_message = mocker.patch("kw.platform.utils.capture_message")

    url = "http://kiwi.com"

    headers = {}
    if sunset_date:
        headers["Sunset"] = sunset_date
    if sunset_link:
        headers["Link"] = '<{}>;rel="sunset"'.format(sunset_link)

    http.register_uri(http.GET, url, body="Hello", adding_headers=headers)

    session = requests.Session()
    session.get(url)

    m_capture_message.assert_not_called()

    wrapt.wrap_function_wrapper(session, "request", wrappers.add_sentry_handler())
    session.get(url)

    if expected_message:
        m_capture_message.assert_called_once_with(
            expected_message.format(sd=sunset_date, sl=sunset_link), level="warning"
        )
    else:
        m_capture_message.assert_not_called()


@pytest.mark.parametrize("message", ["Will be deprecated soon", None])
def test_requests__patch_with_sentry__deprecated_usage(http, mocker, message):
    m_capture_message = mocker.patch("kw.platform.utils.capture_message")

    url = "http://kiwi.com"

    headers = {}
    if message:
        headers["Deprecated-Usage"] = message

    http.register_uri(http.GET, url, body="Hello", adding_headers=headers)

    session = requests.Session()
    session.get(url)

    m_capture_message.assert_not_called()

    wrapt.wrap_function_wrapper(session, "request", wrappers.add_sentry_handler())
    session.get(url)

    if message:
        m_capture_message.assert_called_once_with(message, level="warning")
    else:
        m_capture_message.assert_not_called()
