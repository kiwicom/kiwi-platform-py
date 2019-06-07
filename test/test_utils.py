import pytest

from kw.platform import utils as uut


@pytest.mark.parametrize(
    "user_agent,should_pass",
    [
        ("invalid", False),
        ("mambo/1a (Kiwi.com dev)", True),
        ("mambo/1a (kiwi.com dev)", True),
        ("mambo/1a (kiwicom dev)", False),
        ("zoo/1.0 (Kiwi.com production)", True),
        ("zoo/git-123ad4 (Kiwi.com production) thief requests/2.22", True),
    ],
)
def test_user_agent_re(user_agent, should_pass):
    assert bool(uut.USER_AGENT_RE.match(user_agent)) is should_pass
