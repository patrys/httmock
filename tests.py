import requests
import unittest

from httmock import all_requests, response, urlmatch, with_httmock, HTTMock

@urlmatch(scheme='swallow')
def unmatched_scheme(url, request):
    raise AssertionError('This is outrageous')


@urlmatch(path=r'^never$')
def unmatched_path(url, request):
    raise AssertionError('This is outrageous')


@urlmatch(netloc=r'(.*\.)?google\.com$', path=r'^/$')
def google_mock(url, request):
    return 'Hello from Google'


@urlmatch(scheme='http', netloc=r'(.*\.)?facebook\.com$')
def facebook_mock(url, request):
    return 'Hello from Facebook'


def any_mock(url, request):
    return 'Hello from %s' % (url.netloc,)


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

    def test_netloc_fallback(self):
        with HTTMock(google_mock, facebook_mock):
            r = requests.get('http://google.com/')
        self.assertEqual(r.content, 'Hello from Google')
        with HTTMock(google_mock, facebook_mock):
            r = requests.get('http://facebook.com/')
        self.assertEqual(r.content, 'Hello from Facebook')


class DecoratorTest(unittest.TestCase):

    @with_httmock(any_mock)
    def test_decorator(self):
        r = requests.get('http://example.com/')
        self.assertEqual(r.content, 'Hello from example.com')


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


class ResponseTest(unittest.TestCase):

    def test_response_auto_json(self):
        r = response(0, {'foo':'bar'})
        self.assertTrue(isinstance(r.content, str))
        self.assertEqual(r.content, '{"foo": "bar"}')

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


suite = unittest.TestSuite()
loader = unittest.TestLoader()
suite.addTests(loader.loadTestsFromTestCase(MockTest))
suite.addTests(loader.loadTestsFromTestCase(DecoratorTest))
suite.addTests(loader.loadTestsFromTestCase(AllRequestsDecoratorTest))
suite.addTests(loader.loadTestsFromTestCase(ResponseTest))
