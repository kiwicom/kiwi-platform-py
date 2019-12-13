"""
AIOHTTP
=======

Extensions and helpers for building AIOHTTP-based applications.
"""

from ..utils import ensure_module_is_available


required_module = "aiohttp"
if ensure_module_is_available(required_module):
    from . import utils, monkey
    from .middlewares import user_agent_middleware
    from .monkey import (
        construct_user_agent,
        patch,
        patch_with_sentry,
        patch_with_user_agent,
    )
    from .utils import mandatory_user_agent
    from .session import KiwiClientSession

    __all__ = [
        "construct_user_agent",
        "patch",
        "patch_with_sentry",
        "patch_with_user_agent",
        "mandatory_user_agent",
        "monkey",
        "user_agent_middleware",
        "KiwiClientSession",
        "utils",
    ]
else:
    from .._compat import ModuleNotFoundError  # pylint: disable=redefined-builtin

    raise ModuleNotFoundError(
        "Trying to patch missing module {!r}".format(required_module)
    )
