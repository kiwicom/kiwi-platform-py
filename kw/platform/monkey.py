"""
Monkey Patching
===============
"""

import importlib
import threading


# Define modules and which of them should be patched automatically.
_PATCH_MODULES = {"requests": False, "aiohttp": False}
_PATCHED_MODULES = set()


def _import_module(module_name):
    path = "kw.platform." + module_name
    return importlib.import_module(path)


def _patch_module(module_name):
    with threading.Lock():
        if module_name in _PATCHED_MODULES:
            return False

        module = _import_module(module_name)
        module.patch()

        _PATCHED_MODULES.add(module_name)
        return True


def patch(**patch_modules):
    """Patch specified modules.

    Patches all modules that have been provided as keyword arguments.

    :param patch_modules: keyword arguments of modules that should be patched.
        Use format ``module=True``.
        Possible options are:

        * requests

    Usage::

        from kw.platform import patch

        patch(requests=True)
    """
    modules = [m for m, should_patch in patch_modules.items() if should_patch]
    for module_name in modules:
        if module_name in _PATCH_MODULES.keys():
            _patch_module(module_name)
