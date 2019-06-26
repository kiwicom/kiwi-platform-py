"""
Middlewares
===========
"""


import asyncio
import time

from aiohttp import web

from .. import settings, utils


@web.middleware
async def user_agent_middleware(request, handler):
    """Validate client's User-Agent header and modify response based on that.

    If the User-Agent header is invalid, there are three possible outcomes:

    1. The current time is less then :obj:`settings.KIWI_REQUESTS_SLOWDOWN_DATETIME`,
       do nothing in this case.
    2. The current time is less then :obj:`settings.KIWI_REQUESTS_RESTRICT_DATETIME`,
       slow down the response twice the normal responce time.
    3. The current time is more then :obj:`settings.KIWI_REQUESTS_RESTRICT_DATETIME`,
       refuse the request, return ``HTTP 400`` to the client.

    Usage::

        from aiohttp import web

        from kw.platform.aiohttp.middlewares import user_agent_middleware

        app = web.Application(middlewares=[user_agent_middleware])

    .. warning::

        The middleware slows down requests by calling :meth:`asyncio.sleep()`
        (in the time frame when requests with invalid user-agent are being delayed).
        This can increase busyness and overload a service.
    """
    before_time = time.time()
    response = await handler(request)
    request_duration = time.time() - before_time

    user_agent = utils.UserAgentValidator(request.headers["User-Agent"])

    if user_agent.slowdown:
        await asyncio.sleep(request_duration)
    elif user_agent.restrict:
        raise web.HTTPBadRequest(text=settings.KIWI_RESTRICT_USER_AGENT_MESSAGE)

    return response
