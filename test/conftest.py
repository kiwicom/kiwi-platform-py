import pytest
import requests

from kw.platform.requests import monkey


@pytest.fixture
def app_env_vars(monkeypatch):
    monkeypatch.setenv("APP_NAME", "unittest")
    monkeypatch.setenv("PACKAGE_VERSION", "1.0")
    monkeypatch.setenv("APP_ENVIRONMENT", "test-env")


@pytest.fixture
def patch_requests(mocker, app_env_vars):
    mocker.spy(requests.Session, "request")

    monkey.patch()

    yield

    del requests.__kiwi_platform_patch  # pylint: disable=no-member
