httmock
=======

A mocking library for ``requests`` for Python 2.6, 2.7 and 3.2, 3.3.

Installation
------------
::

    pip install httmock

Usage
-----
You can use it to mock third-party APIs and test libraries that use ``requests`` internally, conditionally using mocked replies with the ``urlmatch`` decorator: ::

    from httmock import urlmatch, HTTMock
    import requests

    @urlmatch(netloc=r'(.*\.)?google\.com$')
    def google_mock(url, request):
        return 'Feeling lucky, punk?'

    with HTTMock(google_mock):
        r = requests.get('http://google.com/')
    print r.content  # 'Feeling lucky, punk?'

The ``all_requests`` decorator doesn't conditionally block real requests. If you return a dictionary, it will map to the ``requests.Response`` object returned: ::

    from httmock import all_requests, HTTMock
    import requests

    @all_requests
    def response_content(url, request):
        return {'status_code': 200,
                'content': 'Oh hai'}

    with HTTMock(response_content):
        r = requests.get('https://foo_bar')

    print r.status_code
    print r.content

If you pass in ``Set-Cookie`` headers, ``requests.Response.cookies`` will contain the values. You can also use ``response`` method directly instead of returning a dict: ::

    from httmock import all_requests, response, HTTMock
    import requests

    @all_requests
    def response_content(url, request):
        headers = {'content-type': 'application/json',
                   'Set-Cookie': 'foo=bar;'}
        content = {'message': 'API rate limit exceeded'}
        return response(403, content, headers, None, 5, request)

    with HTTMock(response_content):
        r = requests.get('https://api.github.com/users/whatever')

    print r.json().get('message')
    print r.cookies['foo']

