import sys


PY2 = sys.version_info[0] == 2
PY35_AND_LESS = sys.version_info[:2] <= (3, 5)


if PY35_AND_LESS:
    ModuleNotFoundError = ImportError  # pylint: disable=redefined-builtin

else:
    ModuleNotFoundError = ModuleNotFoundError


__all__ = ("ModuleNotFoundError",)
