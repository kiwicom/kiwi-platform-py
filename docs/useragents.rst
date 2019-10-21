Mandatory User-Agent
====================

This is a guide on how to implement *Kiwi.com RFC #22: Mandatory User Agents
for service-to-service communication* in Python applications and libraries.

The RFC requires that all HTTP requests made to an internally developed
service must include a ``User-Agent`` header in the following format::

    <service name>/<version> (Kiwi.com <environment>) [<system info>]

In order to achieve this, the RFC also requires that all internal services
must refuse requests which do not comply with this format. Essentially,
the following kinds of changes must be made in all applications and libraries:

1. all HTTP requests made to an internally developed service must include a
   ``User-Agent`` header complying with the KW-RFC-22 format
2. all internally developed services must refuse requests from clients which
   do not comply with the KW-RFC-22 format

The ``kiwi-platform`` library helps to resolve both requirements by
providing:

1. `Making HTTP requests`_ - custom client sessions for making HTTP requests
   and a patching mechanism
2. `Validating client requests`_ - custom middlewares for validating
   client's ``User-Agent`` header

Making HTTP requests
--------------------

The library provides custom sessions for two most used 3rd party libraries:

- `requests <https://requests.readthedocs.io>`_
- `aiohttp <https://aiohttp.readthedocs.io>`_

In order to use them, your application needs to populate the following
environment variables:

- ``APP_NAME`` - name of the application
- ``PACKAGE_VERSION`` - either the git commit hash or a version number,
  for example, ``git-a4f93`` or ``1.0.3``
- ``APP_ENVIRONMENT`` - a string that matches the environment reported,
  for example, to Datadog and Sentry: in most cases, this would be
  ``production``

If you have the variables properly configured, you can use the
:class:`kw.platform.requests.session.KiwiSession` session which automatically
adds a KW-RFC-22 compliant User-Agent to all HTTP requests::

    from kw.platform.requests import KiwiSession

    session = KiwiSession()
    session.get("https://api.example.com")

For async applications using :mod:`aiohttp` as an HTTP client, you can use the
:class:`kw.platform.aiohttp.session.KiwiClientSession` session::

    from kw.platform.aiohttp import KiwiClientSession

    async with KiwiClientSession() as client:
        async with client.get("https://api.example.com") as resp:
            html = await resp.text()
            print(html)

In case you are not using :mod:`requests` or :mod:`aiohttp`, you can still use
our :func:`kw.platform.utils.construct_user_agent` function to construct the
User-Agent::

    import urllib.request

    from kw.platform.utils import construct_user_agent

    request = urllib.request.Request(
        url,
        headers={'User-Agent': construct_user_agent()}
    )
    f = urllib.request.urlopen(request)
    print(f.read().decode('utf-8'))

Monkey patching
~~~~~~~~~~~~~~~

In case you are using :mod:`requests` or :mod:`aiohttp` and it would be too
much work to change all HTTP requests calls to use the proper User-Agent
header, you can also monkey patch :mod:`requests`::

    import requests
    from kw.platform.requests import patch_with_user_agent

    patch_with_user_agent()

    requests.get("https://api.example.com")

or with :mod:`aiohttp`::

    import aiohttp
    from kw.platform.aiohttp import patch_with_user_agent

    patch_with_user_agent()

    with aiohttp.ClientSession() as client:
        ...

You can also use the :func:`kw.platform.requests.patch` or
:func:`kw.platform.aiohttp.patch` functions which provide some additional
patching of the modules like automatic logging of ``Sunset`` HTTP header in
the response body.

HTTP requests in libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~

The correct way to handle KW-RFC-22 in internal libraries
such as ``thief`` is to make it possible for the developer
to prepend their app's ``User-Agent`` header. For example,
this is one way to do it::

    from kw.platform.utils import construct_user_agent
    from kw.python_library import Client

    client = Client(append_user_agent=construct_user_agent())

The ``client`` should make HTTP requests while constructing the ``User-Agent``
similar to this::

    app/1.0 (Kiwi.com production) python_library/1.2 python-requests/2.22.1

The library can also directly use the :func:`construct_user_agent` provided by
``kiwi-platform`` library.

Another way how to handle the KW-RFC-22 in libraries is to make it possible
to pass custom :class:`requests.Session` or :class:`aiohttp.ClientSession`.
The developer could than use the library like this::

    from kw.session.requests import KiwiSession
    from kw.python_library import Client

    client = Client(session=KiwiSession())

Or in the case of :mod:`aiohttp`::

    from kw.session.aiohttp import KiwiClientSession
    from kw.python_library import Client

    client = Client(session=KiwiClientSession)

.. warning::

    Libraries making HTTP requests to internal services should never use
    KW-RFC-22 compliant ``User-Agent`` header by default, each library should
    expect to be provided with a compliant header by the application (either
    via arguments or via environment variables). Otherwise all requests made
    by the library would end up having the same ``User-Agent`` header in the
    logs.

Validating client requests
--------------------------

Internal services must validate requests from other internal applications.
This validation is just checking that the HTTP request to the service contains
KW-RFC-22 compliant ``User-Agent`` header. All non-complying requests must be
refused with the ``HTTP 400 Bad Request`` response, the message of the response
must also explain why the request to the service was denied.

For WSGI applications, the :func:`kw.platform.wsgi.user_agent_middleware`
middleware can be used for validating headers of incoming requests. In Flask,
applying the middleware can be done like this::

    from flask import Flask

    from kw.platform.wsgi import user_agent_middleware

    app = Flask(__name__)
    app.wsgi_app = user_agent_middleware(app.wsgi_app)

    app.run()

Or similarly in Django::

    from django.core.wsgi import get_wsgi_application

    from kw.platform.wsgi import user_agent_middleware

    application = user_agent_middleware(get_wsgi_application())

For async applications built with :mod:`aiohttp`, you can use the
:func:`kw.platform.aiohttp.middlewares.user_agent_middleware` middleware::

    from aiohttp import web

    from kw.platform.aiohttp.middlewares import user_agent_middleware

    app = web.Application(middlewares=[user_agent_middleware])

In case you need to write your own middleware for the validation, you can use
the :class:`kw.platform.utils.UserAgentValidator` validator, like this::

    from kw.platform.utils import UserAgentValidator

    if not UserAgentValidator("generic user-agent").is_valid:
        return 400

Note that the middlewares start restricting requests only after reaching
the date configured by :obj:`settings.KIWI_REQUESTS_RESTRICT_DATETIME`.

.. warning::

    The middlewares also start slowing down requests when the date reaches
    :obj:`settings.KIWI_REQUESTS_SLOWDOWN_DATETIME` and if the date is less then
    :obj:`settings.KIWI_REQUESTS_RESTRICT_DATETIME` (the default).
    This can increase busyness and overload a service.
