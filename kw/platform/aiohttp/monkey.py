"""
Monkey Patching
===============
"""

import aiohttp
import wrapt

from ..utils import _add_user_agent, construct_user_agent


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
        "aiohttp", "ClientSession._request", _add_user_agent(user_agent)
    )


def patch():
    """Apply all patches for :mod:`aiohttp` module.

    This will automatically apply:

    * :func:`kw.platform.aiohttp.patch.patch_with_user_agent`
    """
    if getattr(aiohttp, "__kiwi_platform_patch", False):
        # Already patched, skip
        return
    patch_with_user_agent()

    # Mark module as patched
    setattr(aiohttp, "__kiwi_platform_patch", True)
