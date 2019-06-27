"""
Monkey Patching
===============
"""

import requests
import wrapt

from ..utils import construct_user_agent


def _add_user_agent(user_agent=None):
    def _add_headers(func, instance, args, kwargs):
        headers = kwargs.setdefault("headers", {})
        if not headers.get("User-Agent"):
            if user_agent is None:
                # If no user_agent nor env vars has been provided, request can't be
                # patched.
                raise ValueError(
                    "Unable to patch requests 'User-Agent' header. You have to provide"
                    " either environment variables or patch manually using "
                    "functions `construct_user_agent` and `patch_with_user_agent`."
                    "You can find more info in README."
                )
            else:
                headers["User-Agent"] = (
                    user_agent() if callable(user_agent) else user_agent
                )
        return func(*args, **kwargs)

    return _add_headers


def patch_with_user_agent(user_agent=None):
    """Patch :meth:`requests.Session.request` with User-Agent.

    In case `User-Agent` header has not been provided directly to request.
    Add `User-Agent` string constructed by
    :func:`kw.platform.requests.patch.construct_user_agent` as `User-Agent` header.

    :param user_agent: (optional) User-Agent string that will be used as
        `User-Agent` header.
    """
    if user_agent is None:
        user_agent = construct_user_agent

    wrapt.wrap_function_wrapper(
        "requests", "Session.request", _add_user_agent(construct_user_agent)
    )


def patch():
    """Apply all patches for :mod:`requests` module.

    This will automatically apply:

    * :func:`kw.platform.requests.patch.patch_with_user_agent`
    """
    if getattr(requests, "__kiwi_platform_patch", False):
        # Already patched, skip
        return

    patch_with_user_agent()

    # Mark module as patched
    setattr(requests, "__kiwi_platform_patch", True)
