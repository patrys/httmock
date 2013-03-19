import requests
import unittest

from httmock import urlmatch, HTTMock


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

    def test_fallback(self):
        with HTTMock(google_mock, facebook_mock):
            r = requests.get('http://google.com/')
        self.assertEqual(r.content, 'Hello from Google')
        with HTTMock(google_mock, facebook_mock):
            r = requests.get('http://facebook.com/')
        self.assertEqual(r.content, 'Hello from Facebook')
