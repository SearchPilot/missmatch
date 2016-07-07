import argparse
from html.parser import HTMLParser

import requests


class Tag(object):

    def __init__(self, tag, attrs, pos, is_end=False):
        self.tag = tag
        self.attrs = attrs
        self.pos = pos
        self.is_end = is_end

    def __str__(self):
        tmpl = '<{e}{t} {attrs}> ({ln}:{of})'
        attrs = ''.join(['{k}="{v}" '.format(k=a[0], v=a[1]) for a in self.attrs])
        return tmpl.format(
            e='/' if self.is_end else '',
            t=self.tag,
            attrs=attrs,
            ln=self.pos[0],
            of=self.pos[1])


class TagMismatch(object):

    def __init__(self, start_tag, end_tag):
        self.start = start_tag
        self.end = end_tag

    def __str__(self):
        template = "{st} can't be closed by {et}"
        return template.format(st=self.start,
                               et=self.end)


class HTMLMismatchParser(HTMLParser):

    tags = []
    errors = []

    in_head = False

    # https://www.w3.org/TR/html5/syntax.html#void-elements
    void_elements = [
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    ]

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/head
    head_elements = [
        'title', 'base', 'link', 'style', 'meta', 'script', 'noscript'
    ]

    def handle_starttag(self, start, attrs):

        if start not in self.void_elements:
            tag = Tag(start, attrs, self.getpos())
            self.tags.append(tag)

            if self.in_head and start not in self.head_elements:
                print("ERROR")
                msg = "{t} is not valid in {ht}".format(t=tag, ht='<head>')
                print(msg)
                self.errors.append(msg)

            if start == 'head':
                self.in_head = True

    def handle_endtag(self, end):

        if end not in self.void_elements:
            start = self.tags.pop()

            if end == 'head':
                self.in_head = False

            if start.tag != end:
                end_tag = Tag(end, {}, self.getpos(), is_end=True)
                tm = TagMismatch(start, end_tag)
                self.errors.append(tm)

                print("")
                print("ERROR requiring input")
                print("######################")
                print("")
                print(tm)
                print("")
                print("CASE 1)")
                print(tm.end)
                print("... is a rogue end tag - i.e. it was never opened")
                print("Continue as if we never saw it")
                print("")
                print("CASE 2)")
                print(tm.start)
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
