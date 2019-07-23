"""
Session
=======
"""

import warnings

import aiohttp

from ..utils import add_user_agent_header, construct_user_agent


with warnings.catch_warnings():
    # Ignore aiohttp warning discouraging inheritance until there is a better
    # way to do this. See https://github.com/aio-libs/aiohttp/issues/3695
    warnings.simplefilter("ignore")

    class KiwiClientSession(aiohttp.ClientSession):
        """Custom :class:`aiohttp.ClientSession` with all patches applied.

        Usage::

            from kw.platform.aiohttp import KiwiClientSession
            async with KiwiClientSession() as c:
                await c.get('https://kiwi.com')
        """

        async def _request(self, *args, **kwargs):
            headers = kwargs.setdefault("headers", {})
            add_user_agent_header(headers, construct_user_agent)
            response = await super()._request(*args, **kwargs)
            return response
