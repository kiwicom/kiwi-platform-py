"""
Monkey Patching
===============
"""

import aiohttp
import wrapt

from .. import wrappers
from ..utils import construct_user_agent, report_to_sentry


def _add_sentry_handler(sunset_header=True, deprecated_usage_header=True):
    async def _check_headers(func, instance, args, kwargs):
        response = await func(*args, **kwargs)
        report_to_sentry(
            response,
            sunset_header=sunset_header,
            deprecated_usage_header=deprecated_usage_header,
        )
        return response

    return _check_headers


def patch_with_user_agent(user_agent=None):
    """Patch :meth:`aiohttp.ClientSession._request` with User-Agent.

    In case `User-Agent` header has not been provided directly to request.
    Add `User-Agent` string constructed by
    :func:`kw.platform.aiohttp.patch.construct_user_agent` as `User-Agent` header.

    :param user_agent: (optional) User-Agent string that will be used as
        `User-Agent` header.
    """
    if user_agent is None:
        user_agent = construct_user_agent

    wrapt.wrap_function_wrapper(
        "aiohttp", "ClientSession._request", wrappers.add_user_agent(user_agent)
    )


def patch_with_sentry(sunset_header=True, deprecated_usage_header=True):
    """Patch :meth:`aiohttp.ClientSession._request` to create events in Sentry.

    If the HTTP response contains, for example, the ``Sunset`` HTTP header,
    an event is sent to Sentry containing details about the sunset.

    .. info::

        The patch takes effect only if
        `Sentry SDK <https://github.com/getsentry/sentry-python>`_ is installed
        and properly configured.

    :param sunset_header: (optional) Whether to report the presence of the ``Sunset``
        header, :obj:`True` by default.
    :param deprecated_usage_header: (optional) Whether to report the presence of the
        ``Deprecated-Usage`` header, :obj:`True` by default.
    """
    wrapt.wrap_function_wrapper(
        "aiohttp",
        "ClientSession._request",
        _add_sentry_handler(
            sunset_header=sunset_header, deprecated_usage_header=deprecated_usage_header
        ),
    )


def patch():
    """Apply all patches for :mod:`aiohttp` module.

    This will automatically apply:

    * :func:`kw.platform.aiohttp.patch.patch_with_user_agent`
    * :func:`kw.platform.aiohttp.patch.patch_with_sentry`
    """
    if getattr(aiohttp, "__kiwi_platform_patch", False):
        # Already patched, skip
        return

    patch_with_user_agent()
    patch_with_sentry()

    # Mark module as patched
    setattr(aiohttp, "__kiwi_platform_patch", True)
