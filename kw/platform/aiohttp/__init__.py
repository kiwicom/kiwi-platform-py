"""
AIOHTTP
=======

Extensions and helpers for building AIOHTTP-based applications.
"""

from ..utils import ensure_module_is_available
from .middlewares import user_agent_middleware


required_module = "aiohttp"
if ensure_module_is_available(required_module):
    from .monkey import construct_user_agent, patch, patch_with_user_agent
    from .session import KiwiClientSession

    __all__ = [
        "user_agent_middleware",
        "KiwiClientSession",
        "construct_user_agent",
        "patch_with_user_agent",
        "patch",
    ]
else:
    from .._compat import ModuleNotFoundError  # pylint: disable=redefined-builtin

    raise ModuleNotFoundError(
        "Trying to patch missing module {!r}".format(required_module)
    )
