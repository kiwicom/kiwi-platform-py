import httpretty
import pytest
import requests

from kw.platform import requests as uut


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


def test_kiwi_session(http, patch_requests):
    http.register_uri(http.GET, URL, body="Kiwi.com frontpage")
    resp = uut.KiwiSession().get(URL)
    assert resp.request.headers["User-Agent"] == "unittest/1.0 (Kiwi.com test-env)"


def test_requests_patched(http, patch_requests):
    http.register_uri(http.GET, URL, body="Kiwi.com frontpage")

    res = requests.get(URL)

    assert res.request.headers["User-Agent"] == "unittest/1.0 (Kiwi.com test-env)"
    assert getattr(requests, "__kiwi_platform_patch") is True


def test_requests_not_patched(http):
    http.register_uri(http.GET, URL, body="Kiwi.com frontpage")

    res = requests.get(URL)

    assert "requests" in res.request.headers["User-Agent"]
    assert not hasattr(requests, "__kiwi_platform_patch")
