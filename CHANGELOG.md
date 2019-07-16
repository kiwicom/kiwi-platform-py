# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.2.0 (2019-07-16)

### Added

-   WSGI middleware `kw.platform.wsgi.user_agent_middleware` for delaying or
    rejecting requests which are not KW-RFC-22 compliant.
-   `kw.platform.aiohttp` module and a middleware for delaying or
    rejecting requests which are not KW-RFC-22 compliant.
-   `kw.platform.requests` module which contains:
    -   monkey patching mechanism which patches the `requests` library to add KW-RFC-22
        compliant user agent to all HTTP requests
    -   custom `kw.platform.requests.KiwiSession`
-   Sphinx to generate documentation and deploy it on
    [readthedocs.org](https://kiwi-platform-py.readthedocs.io)

### Changed

-   Migrated the project to use Poetry for package management.

## 0.1.0 (2019-05-29)

-   Initial release, with a completely empty package.
