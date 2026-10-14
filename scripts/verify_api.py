"""Check the HTTP response against the lab's deterministic seed procedure."""
import json
import random
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


def verify(base_url):
    rng = random.Random(24)
    a1, a2, a3 = (rng.uniform(-5, 5) for _ in range(3))
    b = rng.uniform(-10, 10)
    for x1, x2, x3 in [(2, 3, 1), (0, 0, 0), (-2, 1.5, 4)]:
        query = urlencode(dict(x1=x1, x2=x2, x3=x3))
        with urlopen(f'{base_url}/predict?{query}', timeout=10) as response:
            if response.headers.get_content_type() != 'application/json':
                raise AssertionError('Expected application/json')
            result = json.load(response)
        expected = round(a1 * x1 + a2 * x2 + a3 * x3 + b, 2)
        if result.get('registration number') != 'FA23-BDS-024':
            raise AssertionError(f'Incorrect registration number: {result}')
        if result.get('prediction') != expected:
            raise AssertionError(f'Expected {expected}, received {result}')
        print(f'PASS ({x1}, {x2}, {x3}): {result}')

    try:
        urlopen(f'{base_url}/predict?x1=invalid&x2=3&x3=1', timeout=10)
    except HTTPError as error:
        if error.code != 400:
            raise
        print('PASS invalid input returns HTTP 400')
    else:
        raise AssertionError('Invalid input should return HTTP 400')


if __name__ == '__main__':
    verify((sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5000').rstrip('/'))
