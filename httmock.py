from functools import wraps
import datetime
from requests import cookies
import json
import re
import requests
from requests import structures
import sys
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

if sys.version_info >= (3, 0, 0):
    basestring = str


class Headers(object):
    def __init__(self, res):
        self.headers = res.headers

    def get_all(self, name, failobj=None):
        return self.getheaders(name)

    def getheaders(self, name):
        return [self.headers.get(name)]


def response(status_code=200, content='', headers=None, reason=None, elapsed=0,
             request=None):
    res = requests.Response()
    res.status_code = status_code
    if isinstance(content, dict):
        if sys.version_info[0] == 3:
            content = bytes(json.dumps(content), 'utf-8')
        else:
            content = json.dumps(content)
    res._content = content
    res._content_consumed = content
    res.headers = structures.CaseInsensitiveDict(headers or {})
    res.reason = reason
    res.elapsed = datetime.timedelta(elapsed)
    res.request = request
    if hasattr(request, 'url'):
        res.url = request.url
        if isinstance(request.url, bytes):
            res.url = request.url.decode('utf-8')
    if 'set-cookie' in res.headers:
        res.cookies.extract_cookies(cookies.MockResponse(Headers(res)),
                                    cookies.MockRequest(request))

    # normally this closes the underlying connection,
    #  but we have nothing to free.
    res.close = lambda *args, **kwargs: None

    return res


def all_requests(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner


def urlmatch(scheme=None, netloc=None, path=None, method=None):
    def decorator(func):
        @wraps(func)
        def inner(self_or_url, url_or_request, *args, **kwargs):
            if isinstance(self_or_url, urlparse.SplitResult):
                url = self_or_url
                request = url_or_request
            else:
                url = url_or_request
                request = args[0]
            if scheme is not None and scheme != url.scheme:
                return
            if netloc is not None and not re.match(netloc, url.netloc):
                return
            if path is not None and not re.match(path, url.path):
                return
            if method is not None and method.upper() != request.method:
                return
            return func(self_or_url, url_or_request, *args, **kwargs)
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
    STATUS_CODE = 200

    def __init__(self, *handlers):
        self.handlers = handlers

    def __enter__(self):
        self._real_session_send = requests.Session.send

        def _fake_send(session, request, **kwargs):
            response = self.intercept(request)
            if isinstance(response, requests.Response):
                # this is pasted from requests to handle redirects properly:
                kwargs.setdefault('stream', session.stream)
                kwargs.setdefault('verify', session.verify)
                kwargs.setdefault('cert', session.cert)
                kwargs.setdefault('proxies', session.proxies)

                allow_redirects = kwargs.pop('allow_redirects', True)
                stream = kwargs.get('stream')
                timeout = kwargs.get('timeout')
                verify = kwargs.get('verify')
                cert = kwargs.get('cert')
                proxies = kwargs.get('proxies')

                gen = session.resolve_redirects(
                    response,
                    request,
                    stream=stream,
                    timeout=timeout,
                    verify=verify,
                    cert=cert,
                    proxies=proxies)

                history = [resp for resp in gen] if allow_redirects else []

                if history:
                    history.insert(0, response)
                    response = history.pop()
                    response.history = tuple(history)
                return response

            return self._real_session_send(session, request, **kwargs)
        requests.Session.send = _fake_send
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        requests.Session.send = self._real_session_send

    def intercept(self, request):
        url = urlparse.urlsplit(request.url)
        res = first_of(self.handlers, url, request)
        if isinstance(res, requests.Response):
            return res
        elif isinstance(res, dict):
            return response(res.get('status_code'),
                            res.get('content'),
                            res.get('headers'),
                            res.get('reason'),
                            res.get('elapsed', 0),
                            request)
        elif isinstance(res, basestring):
            return response(content=res)
        elif res is None:
            return None
        else:
            raise TypeError(
                "Dont know how to handle response of type {}".format(type(res)))


def with_httmock(*handlers):
    mock = HTTMock(*handlers)

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            with mock:
                return func(*args, **kwargs)
        return inner
    return decorator
