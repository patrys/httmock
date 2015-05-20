import requests
import sys
import unittest

from httmock import all_requests, response, urlmatch, with_httmock, HTTMock


@urlmatch(scheme='swallow')
def unmatched_scheme(url, request):
    raise AssertionError('This is outrageous')


@urlmatch(path=r'^never$')
def unmatched_path(url, request):
    raise AssertionError('This is outrageous')


@urlmatch(method='post')
def unmatched_method(url, request):
    raise AssertionError('This is outrageous')


@urlmatch(netloc=r'(.*\.)?google\.com$', path=r'^/$')
def google_mock(url, request):
    return 'Hello from Google'


@urlmatch(scheme='http', netloc=r'(.*\.)?facebook\.com$')
def facebook_mock(url, request):
    return 'Hello from Facebook'


def any_mock(url, request):
    return 'Hello from %s' % (url.netloc,)


def example_400_response(url, response):
    r = requests.Response()
    r.status_code = 400
    r._content = 'Bad request.'
    return r


class MockTest(unittest.TestCase):

    def test_return_type(self):
        with HTTMock(any_mock):
            r = requests.get('http://domain.com/')
        self.assertTrue(isinstance(r, requests.Response))

    def test_scheme_fallback(self):
        with HTTMock(unmatched_scheme, any_mock):
            r = requests.get('http://example.com/')
        self.assertEqual(r.content, 'Hello from example.com')

    def test_path_fallback(self):
        with HTTMock(unmatched_path, any_mock):
            r = requests.get('http://example.com/')
        self.assertEqual(r.content, 'Hello from example.com')

    def test_method_fallback(self):
        with HTTMock(unmatched_method, any_mock):
            r = requests.get('http://example.com/')
        self.assertEqual(r.content, 'Hello from example.com')

    def test_netloc_fallback(self):
        with HTTMock(google_mock, facebook_mock):
            r = requests.get('http://google.com/')
        self.assertEqual(r.content, 'Hello from Google')
        with HTTMock(google_mock, facebook_mock):
            r = requests.get('http://facebook.com/')
        self.assertEqual(r.content, 'Hello from Facebook')

    def test_400_response(self):
        with HTTMock(example_400_response):
            r = requests.get('http://example.com/')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.content, 'Bad request.')

    def test_real_request_fallback(self):
        with HTTMock(any_mock):
            with HTTMock(google_mock, facebook_mock):
                r = requests.get('http://example.com/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Hello from example.com')

    def test_invalid_intercept_response_raises_value_error(self):
        @all_requests
        def response_content(url, request):
            return -1
        with HTTMock(response_content):
            self.assertRaises(TypeError, requests.get, 'http://example.com/')


class DecoratorTest(unittest.TestCase):

    @with_httmock(any_mock)
    def test_decorator(self):
        r = requests.get('http://example.com/')
        self.assertEqual(r.content, 'Hello from example.com')

    @with_httmock(any_mock)
    def test_iter_lines(self):
        r = requests.get('http://example.com/')
        self.assertEqual(list(r.iter_lines()),
                         ['Hello from example.com'])


class AllRequestsDecoratorTest(unittest.TestCase):

    def test_all_requests_response(self):
        @all_requests
        def response_content(url, request):
            return {'status_code': 200, 'content': 'Oh hai'}
        with HTTMock(response_content):
            r = requests.get('https://foo_bar')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Oh hai')

    def test_all_str_response(self):
        @all_requests
        def response_content(url, request):
            return 'Hello'
        with HTTMock(response_content):
            r = requests.get('https://foo_bar')
        self.assertEqual(r.content, 'Hello')


class AllRequestsMethodDecoratorTest(unittest.TestCase):
    @all_requests
    def response_content(self, url, request):
        return {'status_code': 200, 'content': 'Oh hai'}

    def test_all_requests_response(self):
        with HTTMock(self.response_content):
            r = requests.get('https://foo_bar')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, 'Oh hai')

    @all_requests
    def string_response_content(self, url, request):
        return 'Hello'

    def test_all_str_response(self):
        with HTTMock(self.string_response_content):
            r = requests.get('https://foo_bar')
        self.assertEqual(r.content, 'Hello')


class UrlMatchMethodDecoratorTest(unittest.TestCase):
    @urlmatch(netloc=r'(.*\.)?google\.com$', path=r'^/$')
    def google_mock(self, url, request):
        return 'Hello from Google'

    @urlmatch(scheme='http', netloc=r'(.*\.)?facebook\.com$')
    def facebook_mock(self, url, request):
        return 'Hello from Facebook'

    @urlmatch(query=r'.*page=test')
    def query_page_mock(self, url, request):
        return 'Hello from test page'

    def test_netloc_fallback(self):
        with HTTMock(self.google_mock, facebook_mock):
            r = requests.get('http://google.com/')
        self.assertEqual(r.content, 'Hello from Google')
        with HTTMock(self.google_mock, facebook_mock):
            r = requests.get('http://facebook.com/')
        self.assertEqual(r.content, 'Hello from Facebook')

    def test_query(self):
        with HTTMock(self.query_page_mock, self.google_mock):
            r = requests.get('http://google.com/?page=test')
            r2 = requests.get('http://google.com/')
        self.assertEqual(r.content, 'Hello from test page')
        self.assertEqual(r2.content, 'Hello from Google')


class ResponseTest(unittest.TestCase):

    content = {'name': 'foo', 'ipv4addr': '127.0.0.1'}
    content_list = list(content.keys())

    def test_response_auto_json(self):
        r = response(0, self.content)
        if sys.version_info[0] == 2:
            self.assertTrue(isinstance(r.content, str))
        elif sys.version_info[0] == 3:
            self.assertTrue(isinstance(r.content, bytes))
        else:
            assert False, 'Could not determine Python version'
        self.assertEqual(r.json(), self.content)
        r = response(0, self.content_list)
        self.assertEqual(r.json(), self.content_list)

    def test_response_status_code(self):
        r = response(200)
        self.assertEqual(r.status_code, 200)

    def test_response_headers(self):
        r = response(200, None, {'Content-Type': 'application/json'})
        self.assertEqual(r.headers['content-type'], 'application/json')

    def test_response_cookies(self):
        @all_requests
        def response_content(url, request):
            return response(200, 'Foo', {'Set-Cookie': 'foo=bar;'},
                            request=request)
        with HTTMock(response_content):
            r = requests.get('https://foo_bar')
        self.assertEqual(len(r.cookies), 1)
        self.assertTrue('foo' in r.cookies)
        self.assertEqual(r.cookies['foo'], 'bar')

    def test_response_cookies_stored_in_session(self):
        cookies = 'foo=bar;'

        @all_requests
        def response_content(url, request):
            return response(200, 'Foo', {'Set-Cookie': cookies},
                            request=request)

        session = requests.Session()
        with HTTMock(response_content):
            r = session.get('https://foo_bar')
            self.assertEqual(r.cookies['foo'], 'bar')
            self.assertEqual(session.cookies['foo'], 'bar')
            cookies = 'baz=qux;'
            r = session.get('https://foo_bar')
            self.assertTrue('foo' not in r.cookies)
            self.assertEqual(session.cookies['foo'], 'bar')
            self.assertEqual(session.cookies['baz'], 'qux')

    def test_session_cookies_with_redirect(self):
        @urlmatch(netloc='example.com')
        def get_mock(url, request):
            return {'status_code': 302,
                    'headers': {'Location': 'http://google.com/',
                                'Set-Cookie': 'foo=bar;'}}

        session = requests.Session()
        with HTTMock(get_mock, google_mock):
            r = session.get('http://example.com/')
            self.assertEqual(len(r.history), 1)
            self.assertTrue("foo" not in r.cookies)
            self.assertTrue("foo" in session.cookies)

    def test_python_version_encoding_differences(self):
        # Previous behavior would result in this test failing in Python3 due
        # to how requests checks for utf-8 JSON content in requests.utils with:
        #
        # TypeError: Can't convert 'bytes' object to str implicitly
        @all_requests
        def get_mock(url, request):
            return {'content': self.content,
                    'headers': {'content-type': 'application/json'},
                    'status_code': 200,
                    'elapsed': 5}

        with HTTMock(get_mock):
            response = requests.get('http://foo_bar')
            self.assertEqual(self.content, response.json())

    def test_mock_redirect(self):
        @urlmatch(netloc='example.com')
        def get_mock(url, request):
            return {'status_code': 302,
                    'headers': {'Location': 'http://google.com/'}}

        with HTTMock(get_mock, google_mock):
            response = requests.get('http://example.com/')
            self.assertEqual(len(response.history), 1)
            self.assertEqual(response.content, 'Hello from Google')
