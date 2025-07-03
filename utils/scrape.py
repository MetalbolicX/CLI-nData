#!/usr/bin/env python

"""
This script extracts HTML elements using an XPath query or CSS3 selector.

Example usage:
$ curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be 'table.wikitable > tbody > tr  > td > b > a'

Dependencies:
- lxml
- cssselect (optional)

Author: http://jeroenjanssens.com
"""

import sys
import argparse
from lxml import etree
from typing import List, Union


def main() -> int:
    """
    Main function to parse arguments and extract HTML elements based on XPath or CSS3 selectors.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('html', nargs='?', type=argparse.FileType('rb'),
                        default=sys.stdin, help="HTML", metavar="HTML")
    parser.add_argument('-a', '--attribute', default="",
                        help="Attribute to extract from tag")
    parser.add_argument('-b', '--include_body_tags', action='store_true', default=False,
                        help="Enclose output with HTML and BODY tags")
    parser.add_argument('-e', '--selectors', default=[], action='append',
                        help="XPath query or CSS3 selector")
    parser.add_argument('-f', '--input_file', default='',
                        help="File to read input from")
    parser.add_argument('-x', '--check_existence', action='store_true', default=False,
                        help="Process return value signifying existence")
    parser.add_argument('-r', '--raw_input', action='store_true', default=False,
                        help="Do not parse HTML before feeding etree (useful"
                        "for escaping CData)")
    args = parser.parse_args()

    args.selectors = [selector.decode('utf-8') if isinstance(selector, bytes) else selector for selector in args.selectors]

    from cssselect import GenericTranslator

    xpath_expressions: List[str] = [selector if selector.startswith('//') else GenericTranslator().css_to_xpath(selector) for selector in args.selectors]

    html_parser = etree.HTMLParser(encoding='utf-8', recover=True,
                                   strip_cdata=True)

    input_source = open(args.input_file) if args.input_file else args.html
    if args.raw_input:
        document_tree = etree.fromstring(input_source.read())
    else:
        document_tree = etree.parse(input_source, html_parser)

    if args.include_body_tags:
        sys.stdout.write("<!DOCTYPE html>\n<html>\n<body>\n")

    for xpath_expression in xpath_expressions:
        elements: List[Union[str, etree.Element]] = list(document_tree.xpath(xpath_expression))

        if args.check_existence:
            sys.exit(1 if len(elements) == 0 else 0)

        for element in elements:
            if isinstance(element, str):
                element_text = element
            elif not args.attribute:
                element_text = etree.tostring(element)
            else:
                element_text = element.get(args.attribute)
            if element_text is not None:
                if isinstance(element_text, bytes):
                    element_text = element_text.decode('utf-8')  # Decode bytes to string
                sys.stdout.write(element_text.strip() + "\t")

    if args.include_body_tags:
        sys.stdout.write("</body>\n</html>")

    sys.stdout.write('\n')
    sys.stdout.flush()

    return 0


if __name__ == "__main__":
    exit(main())
