import pytest

from kw.platform import utils as uut


def test_ensure_module_is_available():
    assert uut.ensure_module_is_available("requests") is True

    # Should return False for missing module
    assert uut.ensure_module_is_available("pandas") is False


@pytest.mark.parametrize(
    "user_agent,should_pass",
    [
        (None, False),
        ("", False),
        ("invalid", False),
        ("mambo/1a (Kiwi.com dev)", True),
        ("mambo/1a (kiwi.com dev)", True),
        ("mambo/1a (kiwicom dev)", False),
        ("zoo/1.0 (Kiwi.com production)", True),
        ("zoo/git-123ad4 (Kiwi.com production) thief requests/2.22", True),
    ],
)
def test_user_agent_re(user_agent, should_pass):
    assert uut.UserAgentValidator(user_agent).is_valid is should_pass


def test_construct_user_agent(app_env_vars):
    user_agent = uut.construct_user_agent()
    assert user_agent == "unittest/1.0 (Kiwi.com test-env)"

    user_agent = uut.construct_user_agent(
        app_name="different-test",
        package_version="2.0",
        app_environment="different-test-env",
    )
    assert user_agent == "different-test/2.0 (Kiwi.com different-test-env)"


def test_construct_user_agent_missing_args(monkeypatch):
    # Cleanup env vars.
    # Otherwise the 'None' arguments would get overwritten
    monkeypatch.setenv("APP_NAME", "")
    monkeypatch.setenv("PACKAGE_VERSION", "")
    monkeypatch.setenv("APP_ENVIRONMENT", "")

    user_agent_1 = uut.construct_user_agent(
        app_name=None, package_version="2.0", app_environment="different-test-env"
    )
    user_agent_2 = uut.construct_user_agent(
        app_name="different-test",
        package_version=None,
        app_environment="different-test-env",
    )
    user_agent_3 = uut.construct_user_agent(
        app_name="different-test", package_version="2.0", app_environment=None
    )
    for user_agent in (user_agent_1, user_agent_2, user_agent_3):
        assert user_agent is None
