"""
WSGI helpers
============

Various helpers for WSGI applications.
"""

import time

import webob
from webob.dec import wsgify

from . import settings, utils


def _refuse_request(req, app):
    return webob.exc.HTTPBadRequest(settings.KIWI_RESTRICT_USER_AGENT_MESSAGE)


def _slowdown_request(req, app):
    before_time = time.time()
    resp = req.get_response(app)
    seconds = time.time() - before_time
    time.sleep(seconds)
    return resp


def _validate_user_agent(req, app):
    user_agent = utils.UserAgentValidator(req.user_agent)

    if user_agent.slowdown:
        return _slowdown_request(req, app)
    elif user_agent.restrict:
        return _refuse_request(req, app)

    return app


#: Validate client's User-Agent header and modify response based on that.
#:
#: If the User-Agent header is invalid, there are three possible outcomes:
#:
#: 1. The current time is less then :obj:`settings.KIWI_REQUESTS_SLOWDOWN_DATETIME`,
#:    do nothing in this case.
#: 2. The current time is less then :obj:`settings.KIWI_REQUESTS_RESTRICT_DATETIME`,
#:    slow down the response twice the normal responce time.
#: 3. The current time is more then :obj:`settings.KIWI_REQUESTS_RESTRICT_DATETIME`,
#:    refuse the request, return ``HTTP 400`` to the client.
#:
#: Usage::
#:
#:     from your_app import wsgi_app
#:
#:     wsgi_app = user_agent_middleware(wsgi_app)
#:
#: For example, in Flask, the middleware can be applied like this::
#:
#:     from flask import Flask
#:
#:     app = Flask(__name__)
#:     app.wsgi_app = user_agent_middleware(app)
#:
#:     app.run()
#:
#: In Django, you can apply the middleware like this::
#:
#:     from django.core.wsgi import get_wsgi_application
#:
#:     application = user_agent_middleware(get_wsgi_application())
#:
#: For more information see
#: `Django docs <https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/>`_.
#:
#: .. warning::
#:
#:     The middleware slows down requests by calling :meth:`time.sleep()`
#:     (in the time frame when requests with invalid user-agent are being delayed).
#:     This can increase worker busyness which can overload a service.
user_agent_middleware = wsgify.middleware(_validate_user_agent)
