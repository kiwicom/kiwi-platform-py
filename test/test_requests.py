import httpretty
import pytest
import requests

from kw.platform import requests as uut


@pytest.fixture
def http():
    httpretty.enable()
    try:
        yield httpretty
    finally:
        httpretty.disable()
        httpretty.reset()


def test_kiwi_session(http, patch_requests):
    url = "http://kiwi.com"
    http.register_uri(http.GET, url, body="Kiwi.com frontpage")

    resp = uut.KiwiSession().get(url)
    assert resp.request.headers["User-Agent"] == "unittest/1.0 (Kiwi.com test-env)"


def test_requests_patched(http, patch_requests):
    url = "http://kiwi.com"
    http.register_uri(http.GET, url, body="Kiwi.com frontpage")

    res = requests.get(url)

    assert res.request.headers["User-Agent"] == "unittest/1.0 (Kiwi.com test-env)"
    assert getattr(requests, "__kiwi_platform_patch") is True


def test_requests_not_patched(http):
    url = "http://kiwi.com"
    http.register_uri(http.GET, url, body="Kiwi.com frontpage")

    res = requests.get(url)

    assert "requests" in res.request.headers["User-Agent"]
    assert not hasattr(requests, "__kiwi_platform_patch")
