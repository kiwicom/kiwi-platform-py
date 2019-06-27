from .utils import add_user_agent_header, report_to_sentry


def add_user_agent(user_agent=None):
    def _add_headers(func, instance, args, kwargs):
        headers = kwargs.setdefault("headers", {})
        add_user_agent_header(headers, user_agent)
        return func(*args, **kwargs)

    return _add_headers


def add_sentry_handler(sunset_header=True, deprecated_usage_header=True):
    def _check_headers(func, instance, args, kwargs):
        response = func(*args, **kwargs)
        report_to_sentry(
            response,
            sunset_header=sunset_header,
            deprecated_usage_header=deprecated_usage_header,
        )
        return response

    return _check_headers
