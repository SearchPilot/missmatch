import re

import requests


class FakeResponse(object):

    def add_debug_message(self, message):
        pass


def get_response(url, extra_headers):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'x-bypass-adapation': 'on'
    }
    headers.update(extra_headers)

    r = requests.get(
        url, headers=headers, allow_redirects=False)

    response = FakeResponse()
    response.headers = r.headers
    response.body = r.content
    response.status_code = r.status_code

    return response


def slug_from_url(url):
    """Return something that can be used as a filename based on the given url
    """

    find_replaces = [
        ('http(s)?://', ''),
        ('\.', '-'),
        ('/', '-'),
    ]

    for find, replace in find_replaces:
        url = re.sub(find, replace, url)

    return url
