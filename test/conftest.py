import pytest


@pytest.fixture
def app_env_vars(monkeypatch):
    monkeypatch.setenv("APP_NAME", "unittest")
    monkeypatch.setenv("PACKAGE_VERSION", "1.0")
    monkeypatch.setenv("APP_ENVIRONMENT", "test-env")
