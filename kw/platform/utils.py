"""
Utils
=====
"""

import re
from datetime import datetime

from dateutil.parser import parse

from . import settings


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
