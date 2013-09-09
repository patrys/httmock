httmock
=======

A mocking library for `requests`. You can use it to mock third-party APIs and 
test libraries that use `requests` internally.

Installation
------------

    pip install httmock
    
Usage
-----

```python
from httmock import urlmatch, HTTMock
import requests

@urlmatch(netloc=r'(.*\.)?google\.com$')
def google_mock(url, request):
    return 'Feeling lucky, punk?'

with HTTMock(google_mock):
    r = requests.get('http://google.com/')
print r.content  # 'Feeling lucky, punk?'
```
