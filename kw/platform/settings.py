"""
Settings
========

Configuration of this library.
"""

import os
from distutils.util import strtobool


#: Datetime when to start slowing down requests from services which do not comply with
#: the ``KW-RFC-22`` standard. See :obj:`kw.platform.wsgi.user_agent_middleware`.
KIWI_REQUESTS_SLOWDOWN_DATETIME = os.getenv(
    "KIWI_REQUESTS_SLOWDOWN_DATETIME", "2019-07-24T13:00:00"
)

#: Datetime when to start refusing requests from services which do not comply with
#: the ``KW-RFC-22`` standard. See :obj:`kw.platform.wsgi.user_agent_middleware`.
KIWI_REQUESTS_RESTRICT_DATETIME = os.getenv(
    "KIWI_REQUESTS_RESTRICT_DATETIME", "2019-08-01T13:00:00"
)

#: Status message sent in response to requests with invalid `User-Agent`.
KIWI_RESTRICT_USER_AGENT_MESSAGE = "Invalid User-Agent: does not comply with KW-RFC-22"

#: Enable inspection of requests' User-Agent header and their restriction if not
#: compliant with ``KW-RFC-22``, ``True`` by default.
KIWI_ENABLE_RESTRICTION_OF_REQUESTS = strtobool(
    os.getenv("KIWI_ENABLE_RESTRICTION_OF_REQUESTS", "true")
)
