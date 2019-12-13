"""
Utils
=====
"""

import importlib
import logging
import os
import re
from datetime import datetime

from dateutil.parser import parse

from . import settings
from ._compat import ModuleNotFoundError  # pylint: disable=redefined-builtin


try:
    import sentry_sdk

    sentry_sdk_enabled = True
except ImportError:
    sentry_sdk_enabled = False


USER_AGENT_RE = re.compile(
    r"^(?P<name>\S.+?)\/(?P<version>\S.+?) "
    r"\([Kk]iwi\.com (?P<environment>\S.+?)\)(?: ?(?P<system_info>.*))$"
)
REQ_SLOWDOWN_DATETIME = parse(settings.KIWI_REQUESTS_SLOWDOWN_DATETIME)
REQ_RESTRICT_DATETIME = parse(settings.KIWI_REQUESTS_RESTRICT_DATETIME)


class UserAgentValidator:
    def __init__(self, value):
        self.value = value
        self.is_valid = bool(self.value and USER_AGENT_RE.match(self.value))

    @property
    def ok(self):
        return datetime.utcnow() < REQ_SLOWDOWN_DATETIME or self.is_valid

    @property
    def slowdown(self):
        if not settings.KIWI_ENABLE_RESTRICTION_OF_REQUESTS:
            return False
        return not self.ok and datetime.utcnow() < REQ_RESTRICT_DATETIME

    @property
    def restrict(self):
        if not settings.KIWI_ENABLE_RESTRICTION_OF_REQUESTS:
            return False
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


def capture_message(message, level="info"):
    """Capture mesage to Sentry if Sentry SDK is installed, otherwise use logging.

    :param message: Message to capture.
    :param level: Level of the message, ``info`` by default.
    """
    if sentry_sdk_enabled:
        sentry_sdk.capture_message(message, level=level)
    else:
        logging.warning("Sentry SDK not configured.")
        getattr(logging, level)(message)


def report_to_sentry(response, sunset_header=True, deprecated_usage_header=True):
    """Report response headers to Sentry.

    Reports the following headers:

    - ``Sunset`` or ``sunset`` relation type in ``Link`` header
    - ``Deprecated-Usage``

    :param sunset_header: Whether to report the ``Sunset`` header.
    :param deprecated_usage_header: Whether to report the ``Deprecated-Usage`` header.
    """
    if sunset_header:
        sunset_warning = ""

        if "Sunset" in response.headers:
            sunset_warning += (
                "The Sunset header found in the HTTP response: "
                "{}".format(response.headers["Sunset"])
            )
        if "sunset" in response.links:
            if sunset_warning:
                sunset_warning += ", additional info: "
            else:
                sunset_warning += (
                    "The Sunset Link relation type found in the HTTP response: "
                )
            sunset_warning += str(response.links["sunset"]["url"])

        if sunset_warning:
            capture_message(sunset_warning, level="warning")

    if deprecated_usage_header:
        deprecated_usage_warning = response.headers.get("Deprecated-Usage")

        if deprecated_usage_warning:
            capture_message(deprecated_usage_warning, level="warning")


def httpdate(dt):
    """Return a string representation of a date according to RFC 1123 (HTTP/1.1).

    The supplied date must be in UTC.

    :param dt: Datetime object in UTC.
    :type dt: datetime
    :rtype: str
    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ][dt.month - 1]
    return (
        "{weekday}, {dt.day:02d} {month} {dt.year:04d} "
        "{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} GMT"
    ).format(weekday=weekday, month=month, dt=dt)
