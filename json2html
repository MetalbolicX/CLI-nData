#!/usr/bin/env python3
import json
import argparse
import os
import html
from typing import Any, List, Dict


def json_2_html(input_file: str, suppress: bool) -> None:
    """
    Convert a JSON file to an HTML table and print it to the console.

    This function reads a JSON file, processes its contents, and generates
    an HTML table. Rows can be suppressed from being printed using the suppress flag.

    Args:
        input_file (str): Path to the input JSON file.
        suppress (bool): If True, suppress printing rows to the console.

    Returns:
        None
    """
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        return

    with open(input_file, "r", encoding="utf-8") as jsonfile:
        try:
            data = json.load(jsonfile)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON file: {e}")
            return

    # Validate JSON structure
    if not isinstance(data, list):
        print("Error: JSON file must contain an array of objects.")
        return

    if len(data) == 0:
        print("Error: JSON file is empty.")
        return

    # Extract headers from the keys of the first object
    headers = list(data[0].keys())

    # Start HTML generation
    print("<!DOCTYPE html>")
    print("<html>")
    print("<head>")
    print("<title>JSON to HTML</title>")
    print("</head>")
    print("<body>")
    print("<table>")
    print("<thead>")
    print("<tr>")
    for header in headers:
        print(f"<th>{html.escape(header)}</th>")
    print("</tr>")
    print("</thead>")
    print("<tbody>")

    # Process rows one by one
    for row in data:
        if not suppress:
            print("<tr>")
            for header in headers:
                value = row.get(header, "")
                print(f"<td>{html.escape(str(value))}</td>")
            print("</tr>")

    print("</tbody>")
    print("</table>")
    print("</body>")
    print("</html>")


if __name__ == "__main__":
    """
    Entry point for the script.

    Parses command-line arguments and calls the json_to_html function
    to convert the specified JSON file to HTML.
    """
    parser = argparse.ArgumentParser(description="Convert JSON to HTML.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("-s", "--suppress", action="store_true", help="Suppress printing each row to the screen.")
    args = parser.parse_args()

    input_file: str = args.input_file
    suppress: bool = args.suppress

    json_2_html(input_file, suppress)