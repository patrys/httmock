from functools import wraps
import re
import requests
import urlparse


def urlmatch(scheme=None, netloc=None, path=None):
    def decorator(func):
        @wraps(func)
        def inner(url, *args, **kwargs):
            if scheme is not None and scheme != url.scheme:
                return
            if netloc is not None and not re.match(netloc, url.netloc):
                return
            if path is not None and not re.match(path, url.path):
                return
            return func(url, *args, **kwargs)
        return inner
    return decorator


def first_of(handlers, *args, **kwargs):
    for handler in handlers:
        res = handler(*args, **kwargs)
        if res is not None:
            return res


class HTTMock(object):
    """
    Acts as a context manager to allow mocking
    """
    def __init__(self, *handlers):
        self.handlers = handlers

    def __enter__(self):
        self._real_session_send = requests.Session.send

        def _fake_send(session, request, **kwargs):
            return (self.intercept(request) or
                    self._real_session_send(session, request, **kwargs))

        requests.Session.send = _fake_send
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        requests.Session.send = self._real_session_send

    def intercept(self, request):
        url = urlparse.urlsplit(request.url)
        res = first_of(self.handlers, url, request)
        if res is not None:
            if isinstance(res, basestring):
                response = requests.Response()
                response._content = res
                return response
            return res


def with_httmock(*handlers):
    mock = HTTMock(*handlers)

    def decorator(func):
        @wraps(func)
	def inner(*args, **kwargs):
            with mock:
                return func(*args, **kwargs)

        return inner

    return decorator
