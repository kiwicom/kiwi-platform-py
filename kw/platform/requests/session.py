"""
Session
=======
"""

import requests

from ..utils import add_user_agent_header, construct_user_agent, report_to_sentry


class KiwiSession(requests.Session):
    """Custom :class:`requests.Session` with all patches applied.

    Usage::

        from kw.platform.requests import KiwiSession
        session = KiwiSession()
        session.get('https://kiwi.com')
    """

    def request(self, *args, **kwargs):
        headers = kwargs.setdefault("headers", {})
        add_user_agent_header(headers, construct_user_agent)
        response = super(KiwiSession, self).request(*args, **kwargs)
        report_to_sentry(response, sunset_header=True, deprecated_usage_header=True)
        return response
