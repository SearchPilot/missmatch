import argparse
from difflib import HtmlDiff
import subprocess

from bs4 import UnicodeDammit
from lxml import etree
import lxml.html.soupparser

from utils import get_response
from utils import slug_from_url

USE_SOUP_THRESHOLD = 0.9
USE_SOUP_FALLBACK = True


def should_use_soup_fallback(old_body, new_body):
    """ Return True If the body of the parsed page is significantly smaller
    than the original (a sign the lxml parsing has failed)
    """

    old_length = len(old_body)
    new_length = len(new_body)
    fraction = float(new_length) / old_length

    fallback = False
    if USE_SOUP_FALLBACK and fraction < USE_SOUP_THRESHOLD:
        fallback = True

    return fallback


def parse_response_soup(body, encoding, request_id):
    """ Use beautiful soup to parse the response

    This parser is slower and only used as a fallback. It is better at handling
    encoding and other malformed html.
    """

    if not encoding:
        dammit = UnicodeDammit(body)
        encoding = dammit.original_encoding

    tree = lxml.html.soupparser.fromstring(body,
                                           features='html5lib',
                                           from_encoding=encoding)

    return tree


def parse_response(body, encoding):
    """ Parse the response into an lxml tree """

    etree_parser = etree.HTMLParser(recover=True, encoding=encoding)
    tree = etree.fromstring(body, parser=etree_parser)

    new_body = etree.tostring(
        tree.getroottree(), method='html', encoding=encoding)

    if should_use_soup_fallback(body, new_body):
        print('Falling back to Soup Parser')
        tree = parse_response_soup(body, encoding)

    return tree


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Parse the url with lxml and show the diff")
    parser.add_argument('url')
    parser.add_argument('--encoding', default='utf-8')
    args = parser.parse_args()

    response = get_response(args.url, {})
    original_body = response.body

    tree = parse_response(body=original_body, encoding=args.encoding)
    parsed_body = etree.tostring(tree, method='html', encoding=args.encoding)

    original_body_lines = original_body.decode('utf-8').splitlines()
    parsed_body_lines = parsed_body.decode('utf-8').splitlines()

    output_file = '{fn}.diff.html'.format(fn=slug_from_url(args.url))
    with(open(output_file, 'w')) as diff_file:

        htmldiff = HtmlDiff(
            wrapcolumn=59, charjunk=lambda c: c in [" ", "\t", "/"])
        diff_html = htmldiff.make_file(
            original_body_lines, parsed_body_lines, context=True)

        diff_file.writelines(diff_html)

    print('opening diff in browser')
    subprocess.call(['open', output_file])
