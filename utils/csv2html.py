#!/usr/bin/env python3
import csv
import argparse
import sys
from typing import List
from tabulate import tabulate


def csv_to_html(input_data: str, delimiter: str, suppress_data: bool) -> str:
    """
    Convert CSV data to a complete HTML document with table.

    Args:
        input_data (str): Raw CSV text to be converted to HTML.
        delimiter (str): The delimiter used in the CSV data.
        suppress_data (bool): If True, suppress data rows (headers only).

    Returns:
        str: Complete HTML document string with table.
    """
    clean_input: str = input_data.strip()
    if not clean_input:
        raise ValueError("CSV data is empty")

    try:
        rows: List[List[str]] = list(csv.reader(clean_input.splitlines(), delimiter=delimiter))
    except csv.Error as e:
        raise ValueError(f"Failed to parse CSV: {e}")

    if not rows:
        raise ValueError("CSV data is empty")

    headers: List[str] = rows[0]
    data_rows: List[List[str]] = rows[1:]

    if not headers or all(not header.strip() for header in headers):
        raise ValueError("No valid headers found in CSV data")

    table_data = [] if suppress_data else data_rows
    html_table: str = tabulate(table_data, headers=headers, tablefmt="html")

    html_document: str = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV to HTML Table</title>
    <style>
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
    <h1>CSV Data Table</h1>
    {html_table}
</body>
</html>"""

    return html_document


def main() -> int:
    """
    Entry point for the script.

    Parses command-line arguments and converts CSV from stdin to HTML.
    """
    parser = argparse.ArgumentParser(description="Convert CSV to HTML using tabulate.")
    parser.add_argument(
        "-d", "--delimiter",
        default=",",
        help="Specify the CSV delimiter (default: ',')"
    )
    parser.add_argument(
        "-s", "--suppress",
        action="store_true",
        help="Suppress data rows (headers only)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    if sys.stdin.isatty():
        print("Error: No input provided. Please pipe CSV data to stdin.", file=sys.stderr)
        return 1

    try:
        input_data: str = sys.stdin.read()
        html_document: str = csv_to_html(input_data, args.delimiter, args.suppress)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as output_file:
                output_file.write(html_document)
            print(f"HTML document written to {args.output}")
        else:
            print(html_document)

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"File error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())