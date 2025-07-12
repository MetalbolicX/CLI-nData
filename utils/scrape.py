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

# Named constants
XPATH_PREFIX = "//"
HTML_DOCTYPE = "<!DOCTYPE html>"
HTML_OPEN_TAGS = "<html>\n<body>"
HTML_CLOSE_TAGS = "</body>\n</html>"
DEFAULT_ENCODING = "utf-8"
SUCCESS_EXIT_CODE = 0
ERROR_EXIT_CODE = 1
ELEMENT_SEPARATOR = "\t"
LINE_SEPARATOR = "\n"
EMPTY_HTML_FALLBACK = b"<html><body></body></html>"

# Move cssselect import to top with error handling
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
    parser = argparse.ArgumentParser(
        description="Extract HTML elements using XPath queries or CSS3 selectors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all links from a webpage
  curl 'https://example.com' -s | scrape -e 'a'

  # Extract href attributes from links
  curl 'https://example.com' -s | scrape -e 'a' -a 'href'

  # Check if elements exist (exit code 0 if found, 1 if not)
  curl 'https://example.com' -s | scrape -e 'div.error' -x

  # Process multiple selectors
  scrape -e 'h1' -e 'h2' -e 'h3' -f page.html
"""
    )

    parser.add_argument("html", nargs="?", type=argparse.FileType("rb"),
                        default=sys.stdin, help="HTML input (default: stdin)", metavar="HTML")
    parser.add_argument("-a", "--attribute", default="",
                        help="Attribute to extract from tag")
    parser.add_argument("-b", "--include_body_tags", action="store_true", default=False,
                        help="Enclose output with HTML and BODY tags")
    parser.add_argument("-e", "--selectors", default=[], action="append",
                        help="XPath query or CSS3 selector (can be used multiple times)")
    parser.add_argument("-f", "--input_file", default="",
                        help="File to read input from")
    parser.add_argument("-x", "--check_existence", action="store_true", default=False,
                        help="Check existence only (exit code 0 if found, 1 if not)")
    parser.add_argument("-r", "--raw_input", action="store_true", default=False,
                        help="Do not parse HTML before feeding etree (useful for escaping CData)")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    return parser


def validate_arguments(args) -> None:
    """
    Validate command line arguments.

    Args:
        args: Parsed command line arguments.

    Raises:
        SystemExit: If validation fails.
    """
    if not args.selectors:
        print("Error: No selectors provided. Use -e to specify at least one selector.", file=sys.stderr)
        print("Use --help for usage examples.", file=sys.stderr)
        sys.exit(ERROR_EXIT_CODE)

    # Check for conflicting options
    if args.input_file and args.html != sys.stdin:
        print("Error: Cannot specify both input file (-f) and HTML argument.", file=sys.stderr)
        sys.exit(ERROR_EXIT_CODE)


def is_xpath_selector(selector: str) -> bool:
    """
    Check if a selector is an XPath expression.

    Args:
        selector: The selector string to check.

    Returns:
        bool: True if the selector is an XPath expression, False otherwise.
    """
    return selector.startswith(XPATH_PREFIX) or selector.startswith("./") or selector.startswith("(")


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
        match selector:
            case _ if is_xpath_selector(selector):
                xpath_expressions.append(selector)
            case _ if not HAS_CSSSELECT:
                print(f"Error: CSS selector '{selector}' provided but cssselect library is not installed.", file=sys.stderr)
                print("Install cssselect with: pip install cssselect", file=sys.stderr)
                sys.exit(ERROR_EXIT_CODE)
            case _:
                try:
                    xpath_expressions.append(GenericTranslator().css_to_xpath(selector))
                except Exception as e:
                    print(f"Error: Invalid CSS selector '{selector}': {e}", file=sys.stderr)
                    sys.exit(ERROR_EXIT_CODE)

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
    html_parser = etree.HTMLParser(encoding=DEFAULT_ENCODING, recover=True)

    try:
        if input_file:
            with open(input_file, "rb") as input_source:
                content = input_source.read()
                if not content:
                    print(f"Warning: Input file '{input_file}' is empty.", file=sys.stderr)
                    content = EMPTY_HTML_FALLBACK

                if is_raw_input:
                    document_tree = etree.fromstring(content)
                else:
                    document_tree = etree.parse(input_source, html_parser)
        else:
            if is_raw_input:
                content = html_source.read()
                if not content:
                    print("Warning: No input data received.", file=sys.stderr)
                    content = EMPTY_HTML_FALLBACK
                document_tree = etree.fromstring(content)
            else:
                document_tree = etree.parse(html_source, html_parser)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(ERROR_EXIT_CODE)
    except PermissionError:
        print(f"Error: Permission denied accessing file '{input_file}'.", file=sys.stderr)
        sys.exit(ERROR_EXIT_CODE)
    except etree.XMLSyntaxError as e:
        print(f"Error: Invalid XML/HTML syntax: {e}", file=sys.stderr)
        sys.exit(ERROR_EXIT_CODE)
    except Exception as e:
        print(f"Error: Failed to parse HTML: {e}", file=sys.stderr)
        sys.exit(ERROR_EXIT_CODE)

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
    element_text = None

    if isinstance(element, str):
        element_text = element
    elif not attribute:
        element_text = etree.tostring(element)
    else:
        element_text = element.get(attribute)

    if element_text and isinstance(element_text, bytes):
        try:
            element_text = element_text.decode(DEFAULT_ENCODING)
        except UnicodeDecodeError:
            element_text = element_text.decode(DEFAULT_ENCODING, errors="replace")

    return element_text


def process_elements(document_tree: etree.ElementTree, xpath_expressions: List[str],
                    attribute: str, check_existence: bool) -> List[str]:
    """
    Process HTML elements based on XPath expressions.

    Args:
        document_tree: Parsed HTML document.
        xpath_expressions: List of XPath expressions to evaluate.
        attribute: Attribute to extract from elements.
        check_existence: Whether to only check for element existence.

    Returns:
        List of extracted text elements.
    """
    extracted_texts: List[str] = []

    for xpath_expression in xpath_expressions:
        try:
            elements: List[Union[str, etree.Element]] = list(document_tree.xpath(xpath_expression))
        except etree.XPathEvalError as e:
            print(f"Error: Invalid XPath expression '{xpath_expression}': {e}", file=sys.stderr)
            sys.exit(ERROR_EXIT_CODE)
        except Exception as e:
            print(f"Error: XPath evaluation failed for '{xpath_expression}': {e}", file=sys.stderr)
            sys.exit(ERROR_EXIT_CODE)

        if check_existence and elements:
            sys.exit(SUCCESS_EXIT_CODE)

        for element in elements:
            element_text: Optional[str] = extract_element_text(element, attribute)

            if element_text:
                # Handle empty strings and whitespace-only content
                stripped_text = element_text.strip()
                if stripped_text:
                    extracted_texts.append(stripped_text)

    return extracted_texts


def write_output(extracted_texts: List[str], include_body_tags: bool) -> None:
    """
    Write the extracted text elements to stdout with proper formatting.

    Args:
        extracted_texts: List of text elements to output.
        include_body_tags: Whether to include HTML wrapper tags.
    """
    try:
        if include_body_tags:
            sys.stdout.write(f"{HTML_DOCTYPE}{LINE_SEPARATOR}{HTML_OPEN_TAGS}{LINE_SEPARATOR}")

        # Improved output formatting - join elements with tabs, end with newline
        if extracted_texts:
            output_line = ELEMENT_SEPARATOR.join(extracted_texts)
            sys.stdout.write(output_line)

        if include_body_tags:
            sys.stdout.write(f"{LINE_SEPARATOR}{HTML_CLOSE_TAGS}")

        sys.stdout.write(LINE_SEPARATOR)
        sys.stdout.flush()
    except BrokenPipeError:
        # Handle broken pipe gracefully (e.g., when piping to head)
        pass
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        sys.exit(ERROR_EXIT_CODE)


def main() -> int:
    """
    Main function to parse arguments and extract HTML elements based on XPath or CSS3 selectors.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    try:
        parser = create_argument_parser()
        args = parser.parse_args()

        # Validate arguments
        validate_arguments(args)

        # Process selectors - handle potential encoding issues
        processed_selectors: List[str] = []
        for selector in args.selectors:
            if isinstance(selector, bytes):
                try:
                    processed_selectors.append(selector.decode(DEFAULT_ENCODING))
                except UnicodeDecodeError:
                    processed_selectors.append(selector.decode(DEFAULT_ENCODING, errors="replace"))
            else:
                processed_selectors.append(selector)

        args.selectors = processed_selectors

        # Convert selectors to XPath expressions
        xpath_expressions = convert_selectors_to_xpath(args.selectors)

        # Parse HTML document
        document_tree = parse_html_document(args.input_file, args.html, args.raw_input)

        # Process elements
        extracted_texts = process_elements(document_tree, xpath_expressions, args.attribute, args.check_existence)

        # Handle existence check
        if args.check_existence:
            return SUCCESS_EXIT_CODE if extracted_texts else ERROR_EXIT_CODE

        # Write output
        write_output(extracted_texts, args.include_body_tags)

        return SUCCESS_EXIT_CODE

    except KeyboardInterrupt:
        print(f"{LINE_SEPARATOR}Interrupted by user.", file=sys.stderr)
        return ERROR_EXIT_CODE
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return ERROR_EXIT_CODE


if __name__ == "__main__":
    exit(main())
