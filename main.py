import argparse
from html.parser import HTMLParser

import requests


class TagMismatch(object):

    def __init__(self, start, end, parser_position):
        self.start = start
        self.end = end
        self.parser_position = parser_position

    def format_start_tag(self):
        attrs_template = '{k}="{v}" '
        attrs = ''.join([attrs_template.format(k=a[0], v=a[1]) for a in self.start[1]])

        start_tag_template = '<{t} {attrs}> ({ln}:{of})'
        return start_tag_template.format(
            t=self.start[0],
            attrs=attrs,
            ln=self.start[2][0],
            of=self.start[2][1])

    def format_end_tag(self):
        return '</{t}> ({ln}:{of})'.format(t=self.end,
                                           ln=self.parser_position[0],
                                           of=self.parser_position[1])

    def __str__(self):

        template = "{st} can't be closed by {et}"
        return template.format(st=self.format_start_tag(),
                               et=self.format_end_tag())


class HTMLMismatchParser(HTMLParser):

    tags = []
    errors = []

    # https://www.w3.org/TR/html5/syntax.html#void-elements
    void_elements = [
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    ]

    def handle_starttag(self, start, attrs):

        if start not in self.void_elements:
            self.tags.append((start, attrs, self.getpos()))

    def handle_endtag(self, end):

        if end not in self.void_elements:
            start = self.tags.pop()

            if start[0] != end:

                tm = TagMismatch(start, end, self.getpos())
                self.errors.append(tm)

                print("")
                print("ERROR")
                print("How should we proceed?")
                print("######################")
                print("")
                print(tm)
                print("")
                print("CASE 1)")
                print(tm.format_end_tag())
                print("... is a rogue end tag - i.e. it was never opened")
                print("Continue as if we never saw it")
                print("")
                print("CASE 2)")
                print(tm.format_start_tag())
                print("... is missing an end tag")
                print("Continue as if we found the close tag")

                print('')
                case = input("Enter 1 or 2: ")

                if case.lower() == '1':
                    # Rogue end tag
                    # Start tag will be closed later, so add it back to the list
                    self.tags.append(start)
                elif case.lower() == '2':
                    # Missing end tag
                    # Compare the current end tag with the next start tag
                    self.handle_endtag(end)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Show tag mismatches on given URL")
    parser.add_argument('url', nargs=1)
    args = parser.parse_args()

    url = args.url.pop()

    r = requests.get(url)
    r.raise_for_status()

    mismatch_parser = HTMLMismatchParser()
    mismatch_parser.feed(r.text)

    if mismatch_parser.errors:
        print("")
        print("There were errors: ")
        print("###################")
        for error in mismatch_parser.errors:
            print(error)
