"""
Requests
========

Extensions and helpers patching kiwi code standards for ``requests`` library.
"""
from ..utils import ensure_module_is_available


required_module = "requests"
if ensure_module_is_available(required_module):
    from .monkey import construct_user_agent, patch, patch_with_user_agent
    from .session import KiwiSession

    __all__ = ["KiwiSession", "construct_user_agent", "patch_with_user_agent", "patch"]
else:
    from .._compat import ModuleNotFoundError  # pylint: disable=redefined-builtin

    raise ModuleNotFoundError(
        "Trying to patch missing module {!r}".format(required_module)
    )
