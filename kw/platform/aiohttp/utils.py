"""
Helpers and Utils
=================
"""

from functools import wraps

from ..utils import httpdate


def set_sunset(response, when=None, info_url=None):
    """Update aiohttp response object with the ``Sunset`` HTTP header.

    :param response: Response object to update.
    :type response: :class:`aiohttp.web.Response`
    :param when: When the Sunset date arrives, must be UTC.
    :type when: datetime
    :param info_url: URL to a page with more information about the Sunset.
    :type info_url: str
    :rtype: :class:`aiohttp.web.Response`
    """
    if info_url:
        link = '<{}>;rel="sunset"'.format(info_url)
        response.headers["Link"] = (
            "{},{}".format(response.headers["Link"], link)
            if response.headers.get("Link")
            else link
        )
    if when:
        response.headers["Sunset"] = httpdate(when)

    return response


def sunset(when=None, info_url=None):
    """A decorator for deprecating views by setting the ``Sunset`` HTTP header.

    Read about the ``Sunset`` header in
    `rfc8594 <https://tools.ietf.org/html/rfc8594>`_.

    Usage::

        @sunset(when=datetime(2019, 8, 1, 10, 0, 0))
        async def index(request):
            return web.Response("Hello, world!")

    :param when: When the Sunset date arrives, must be UTC.
    :type when: datetime
    :param info_url: URL to a page with more information about the Sunset.
    :type info_url: str
    """
    if when is None and info_url is None:
        raise TypeError("function takes at least one argument (0 given)")

    def wrapper(view):
        @wraps(view)
        async def sunset_view(*args, **kwargs):
            response = await view(*args, **kwargs)
            return set_sunset(response, when=when, info_url=info_url)

        return sunset_view

    return wrapper
