"""
Session
=======
"""

import requests
import wrapt

from ..utils import _add_user_agent, construct_user_agent


class KiwiSession(requests.Session):
    """Custom :class:`requests.Session` with all patches applied.

    Usage::

        from kw.platform.requests import KiwiSession
        session = KiwiSession()
        session.get('https://kiwi.com')
    """


wrapt.wrap_function_wrapper(
    KiwiSession, "request", _add_user_agent(construct_user_agent)
)
