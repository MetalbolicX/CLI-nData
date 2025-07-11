#!/usr/bin/env python3

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
from typing import List, Union, Optional

# Fix: Move cssselect import to top with error handling
try:
    from cssselect import GenericTranslator
    HAS_CSSSELECT = True
except ImportError:
    HAS_CSSSELECT = False
    GenericTranslator = None


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("html", nargs="?", type=argparse.FileType("rb"),
                        default=sys.stdin, help="HTML", metavar="HTML")
    parser.add_argument("-a", "--attribute", default="",
                        help="Attribute to extract from tag")
    parser.add_argument("-b", "--include_body_tags", action="store_true", default=False,
                        help="Enclose output with HTML and BODY tags")
    parser.add_argument("-e", "--selectors", default=[], action="append",
                        help="XPath query or CSS3 selector")
    parser.add_argument("-f", "--input_file", default="",
                        help="File to read input from")
    parser.add_argument("-x", "--check_existence", action="store_true", default=False,
                        help="Process return value signifying existence")
    parser.add_argument("-r", "--raw_input", action="store_true", default=False,
                        help="Do not parse HTML before feeding etree (useful"
                        "for escaping CData)")
    return parser


def convert_selectors_to_xpath(selectors: List[str]) -> List[str]:
    """
    Convert CSS selectors to XPath expressions.

    Args:
        selectors: List of CSS selectors or XPath expressions.

    Returns:
        List of XPath expressions.

    Raises:
        SystemExit: If cssselect is not available or selector is invalid.
    """
    xpath_expressions: List[str] = []

    for selector in selectors:
        if selector.startswith("//"):
            xpath_expressions.append(selector)
        else:
            if not HAS_CSSSELECT:
                print(f"Error: CSS selector '{selector}' provided but cssselect library is not installed.", file=sys.stderr)
                print("Install cssselect with: pip install cssselect", file=sys.stderr)
                sys.exit(1)
            try:
                xpath_expressions.append(GenericTranslator().css_to_xpath(selector))
            except Exception as e:
                print(f"Error: Invalid CSS selector '{selector}': {e}", file=sys.stderr)
                sys.exit(1)

    return xpath_expressions


def parse_html_document(input_file: str, html_source, is_raw_input: bool) -> etree.ElementTree:
    """
    Parse HTML document from file or stdin.

    Args:
        input_file: Path to input file, empty string for stdin.
        html_source: HTML source from stdin.
        is_raw_input: Whether to parse as raw input.

    Returns:
        Parsed HTML document tree.

    Raises:
        SystemExit: If file not found or parsing fails.
    """
    html_parser = etree.HTMLParser(encoding="utf-8", recover=True)

    try:
        if input_file:
            with open(input_file, "rb") as input_source:
                if is_raw_input:
                    document_tree = etree.fromstring(input_source.read())
                else:
                    document_tree = etree.parse(input_source, html_parser)
        else:
            input_source = html_source
            if is_raw_input:
                document_tree = etree.fromstring(input_source.read())
            else:
                document_tree = etree.parse(input_source, html_parser)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to parse HTML: {e}", file=sys.stderr)
        sys.exit(1)

    return document_tree


def extract_element_text(element: Union[str, etree.Element], attribute: str) -> Optional[str]:
    """
    Extract text content from an element.

    Args:
        element: HTML element or string.
        attribute: Attribute to extract, empty string for element content.

    Returns:
        Extracted text content or None.
    """
    if isinstance(element, str):
        return element
    elif not attribute:
        element_text = etree.tostring(element)
    else:
        element_text = element.get(attribute)

    if element_text and isinstance(element_text, bytes):
        element_text = element_text.decode("utf-8")

    return element_text


def process_elements(document_tree: etree.ElementTree, xpath_expressions: List[str],
                    attribute: str, check_existence: bool) -> bool:
    """
    Process HTML elements based on XPath expressions.

    Args:
        document_tree: Parsed HTML document.
        xpath_expressions: List of XPath expressions to evaluate.
        attribute: Attribute to extract from elements.
        check_existence: Whether to only check for element existence.

    Returns:
        True if any elements were found, False otherwise.
    """
    has_any_elements: bool = False

    for xpath_expression in xpath_expressions:
        try:
            elements: List[Union[str, etree.Element]] = list(document_tree.xpath(xpath_expression))
        except Exception as e:
            print(f"Error: Invalid XPath expression '{xpath_expression}': {e}", file=sys.stderr)
            sys.exit(1)

        if elements:
            has_any_elements = True

        if check_existence and elements:
            sys.exit(0)

        for element in elements:
            element_text: Optional[str] = extract_element_text(element, attribute)

            if element_text:
                sys.stdout.write(f"{element_text.strip()}\t")

    return has_any_elements


def main() -> int:
    """
    Main function to parse arguments and extract HTML elements based on XPath or CSS3 selectors.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    # Validate selectors
    if not args.selectors:
        print("Error: No selectors provided. Use -e to specify at least one selector.", file=sys.stderr)
        return 1

    # Process selectors
    args.selectors = [
        selector.decode("utf-8") if isinstance(selector, bytes) else selector
        for selector in args.selectors
    ]

    # Convert selectors to XPath expressions
    xpath_expressions = convert_selectors_to_xpath(args.selectors)

    # Parse HTML document
    document_tree = parse_html_document(args.input_file, args.html, args.raw_input)

    # Output HTML header if requested
    if args.include_body_tags:
        sys.stdout.write("<!DOCTYPE html>\n<html>\n<body>\n")

    # Process elements
    has_any_elements = process_elements(document_tree, xpath_expressions, args.attribute, args.check_existence)

    # Handle existence check
    if args.check_existence:
        return 0 if has_any_elements else 1

    # Output HTML footer if requested
    if args.include_body_tags:
        sys.stdout.write("</body>\n</html>")

    sys.stdout.write("\n")
    sys.stdout.flush()

    return 0


if __name__ == "__main__":
    exit(main())
