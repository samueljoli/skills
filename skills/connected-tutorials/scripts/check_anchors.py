#!/usr/bin/env python3
"""Check tutorial anchors, semantic IDs, fragment links, and local assets."""
import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'parents': list(self.stack)}
        self.nodes.append(node)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1]['tag'] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index]['tag'] == tag:
                self.stack = self.stack[:index]
                break


def check(path):
    document = Document()
    document.feed(path.read_text(encoding='utf-8'))
    errors = []
    for attribute in ('id', 'data-step', 'data-layer', 'data-port'):
        values = [n['attrs'][attribute] for n in document.nodes if attribute in n['attrs']]
        for value, count in Counter(values).items():
            if not value or any(c.isspace() for c in value):
                errors.append(f'Invalid {attribute}: {value!r}')
            if count > 1:
                errors.append(f'Duplicate {attribute}: {value!r}')
    ids = {n['attrs']['id'] for n in document.nodes if 'id' in n['attrs']}
    ports = {n['attrs']['data-port'] for n in document.nodes if 'data-port' in n['attrs']}
    steps = [n for n in document.nodes if 'data-step' in n['attrs']]
    passages = [n for n in document.nodes if 'data-connect' in n['attrs']]
    if not steps or not passages:
        errors.append('Expected at least one reading step and connected passage.')
    for required in ('connections', 'focus-label', 'progress', 'stack'):
        if required not in ids:
            errors.append(f'Missing renderer element #{required}')
    for node in document.nodes:
        attrs = node['attrs']
        if 'data-port' in attrs and not any('data-layer' in p['attrs'] for p in node['parents']):
            errors.append(f'Port {attrs["data-port"]!r} has no data-layer owner.')
        if 'data-step' in attrs:
            if not attrs.get('id'):
                errors.append(f'Step {attrs["data-step"]!r} needs an HTML id for navigation.')
            if not any(any(p is node for p in c['parents']) for c in passages):
                errors.append(f'Step {attrs["data-step"]!r} has no connected passage.')
        if 'data-connect' in attrs:
            targets = attrs['data-connect'].split()
            if not targets:
                errors.append('A data-connect attribute has no targets.')
            for port in targets:
                if port not in ports:
                    errors.append(f'Unresolved diagram port {port!r}')
            if not any('data-step' in p['attrs'] for p in node['parents']):
                errors.append('Connected passage has no data-step section.')
            if not any('text-port' in c['attrs'].get('class','').split() and any(p is node for p in c['parents']) for c in document.nodes):
                errors.append('Connected passage has no .text-port child.')
        for attribute in ('href', 'src'):
            value = attrs.get(attribute, '')
            if value.startswith('#') and unquote(value[1:]) not in ids:
                errors.append(f'Broken fragment link {value!r}')
            parsed = urlsplit(value)
            if value and not parsed.scheme and not parsed.netloc and parsed.path and not parsed.path.startswith('/'):
                if not (path.parent / unquote(parsed.path)).exists():
                    errors.append(f'Missing local asset {parsed.path!r}')
    return errors, len(steps), len(ports), len(passages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    args = parser.parse_args()
    errors, steps, ports, passages = check(args.document)
    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        raise SystemExit(1)
    print(f'OK: {steps} steps, {ports} ports, {passages} connected passages; links and assets resolve.')
    print('Browser verification is still required for sticky layout and endpoint alignment.')


if __name__ == '__main__':
    main()
