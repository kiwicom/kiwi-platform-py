"""
Utils
=====
"""

import importlib
import os
import re
from datetime import datetime

from dateutil.parser import parse

from . import settings
from ._compat import ModuleNotFoundError  # pylint: disable=redefined-builtin


USER_AGENT_RE = re.compile(
    r"^(?P<name>\S.+?)\/(?P<version>\S.+?) "
    r"\([Kk]iwi\.com (?P<environment>\S.+?)\)(?: ?(?P<system_info>.*))$"
)
REQ_SLOWDOWN_DATETIME = parse(settings.KIWI_REQUESTS_SLOWDOWN_DATETIME)
REQ_RESTRICT_DATETIME = parse(settings.KIWI_REQUESTS_RESTRICT_DATETIME)


class UserAgentValidator:
    def __init__(self, value):
        self.value = value
        self.is_valid = bool(USER_AGENT_RE.match(self.value))

    @property
    def ok(self):
        return datetime.utcnow() < REQ_SLOWDOWN_DATETIME or self.is_valid

    @property
    def slowdown(self):
        return not self.ok and datetime.utcnow() < REQ_RESTRICT_DATETIME

    @property
    def restrict(self):
        return not self.ok and not self.slowdown


def ensure_module_is_available(module):
    try:
        importlib.import_module(module)
    except ModuleNotFoundError:
        return False
    return True


def construct_user_agent(app_name=None, package_version=None, app_environment=None):
    """Construct User-Agent string from arguments or Environment variables.

    Uses Environment variables as fallback for any argument that has not been provided.
    These Environment variables names are equal to function arguments:

    * ``APP_NAME``
    * ``PACKAGE_VERSION``
    * ``APP_ENVIRONMENT``

    :param app_name: (optional) application name string.
    :param package_version: (optional) version of the package.
    :param app_environment: (optional) name of the environment the app is running in.
        For example ``production``.
    """
    app_name = app_name or os.getenv("APP_NAME")
    package_version = package_version or os.getenv("PACKAGE_VERSION")
    app_environment = app_environment or os.getenv("APP_ENVIRONMENT")
    if all((app_name, package_version, app_environment)):
        user_agent = "{}/{} (Kiwi.com {})".format(
            app_name, package_version, app_environment
        )
    else:
        user_agent = None
    return user_agent


def add_user_agent_header(headers, user_agent):
    if not headers.get("User-Agent"):
        custom_agent = user_agent() if callable(user_agent) else user_agent
        if custom_agent:
            headers["User-Agent"] = custom_agent
        else:
            # If no user_agent nor env vars has been provided, request can't be
            # patched.
            raise ValueError(
                "Unable to patch requests 'User-Agent' header. You have to provide"
                " either environment variables or patch manually using "
                "functions `construct_user_agent` and `patch_with_user_agent`."
                "You can find more info in README."
            )


def _add_user_agent(user_agent=None):
    def _add_headers(func, instance, args, kwargs):
        headers = kwargs.setdefault("headers", {})
        add_user_agent_header(headers, user_agent)
        return func(*args, **kwargs)

    return _add_headers
