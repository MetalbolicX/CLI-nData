#!/usr/bin/env python3
import csv
import argparse
import sys
from typing import List, Optional
from tabulate import tabulate


def csv_to_html(input_data: str, delimiter: str, suppress_data: bool, skip_empty_lines: bool = True, quote_char: str = '"', trim_whitespace: bool = True) -> str:
    """
    Convert CSV data to a complete HTML document with table.

    Args:
        input_data (str): Raw CSV text to be converted to HTML.
        delimiter (str): The delimiter used in the CSV data.
        suppress_data (bool): If True, suppress data rows (headers only).
        skip_empty_lines (bool): If True, skip empty lines in CSV parsing.
        quote_char (str): The quote character used in CSV data.
        trim_whitespace (bool): If True, trim whitespace from all cells.

    Returns:
        str: Complete HTML document string with table.

    Raises:
        ValueError: If CSV data is empty or invalid.
    """
    clean_input: str = input_data.strip()
    if not clean_input:
        raise ValueError("CSV data is empty or contains only whitespace")

    try:
        from io import StringIO
        csv_file = StringIO(clean_input)

        csv_reader = csv.reader(
            csv_file,
            delimiter=delimiter,
            quotechar=quote_char,
            quoting=csv.QUOTE_MINIMAL,
            skipinitialspace=True
        )

        rows: List[List[str]] = []
        for row_number, row in enumerate(csv_reader, start=1):
            # Trim whitespace from all cells if requested
            if trim_whitespace:
                processed_row = [cell.strip() for cell in row]
            else:
                processed_row = row

            # Skip empty rows if requested
            if skip_empty_lines and not any(cell for cell in processed_row):
                continue

            # Only add non-empty rows
            if processed_row:
                rows.append(processed_row)

    except csv.Error as e:
        line_number = getattr(csv_reader, "line_num", "unknown")
        raise ValueError(f"Failed to parse CSV data at line {line_number}: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error during CSV parsing: {e}")

    if not rows:
        raise ValueError("No valid CSV rows found after parsing")

    headers: List[str] = rows[0]
    data_rows: List[List[str]] = rows[1:]

    # Validate headers after trimming
    if not headers or all(not header for header in headers):
        raise ValueError("No valid headers found in CSV data")

    # Validate column consistency and pad/truncate as needed
    expected_columns: int = len(headers)
    normalized_data_rows: List[List[str]] = []

    for row_index, row in enumerate(data_rows, start=2):
        current_columns: int = len(row)

        if current_columns != expected_columns:
            # Normalize rows (pad with empty strings or truncate)
            if current_columns < expected_columns:
                missing_columns = expected_columns - current_columns
                normalized_row = row + [""] * missing_columns
            else:
                normalized_row = row[:expected_columns]

            normalized_data_rows.append(normalized_row)
        else:
            normalized_data_rows.append(row)

    table_data: List[List[str]] = [] if suppress_data else normalized_data_rows

    try:
        html_table: str = tabulate(table_data, headers=headers, tablefmt="html")
    except Exception as e:
        raise ValueError(f"Failed to generate HTML table: {e}")

    html_document: str = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV to HTML Table</title>
    <link rel="stylesheet" href="https://unpkg.com/@colinaut/action-table/dist/action-table.css">
    <script type="module" src="https://unpkg.com/@colinaut/action-table/dist/index.js"></script>
</head>
<body>
    <h1>CSV Data Table</h1>
    <action-table>
        {html_table}
    </action-table>
</body>
</html>"""

    return html_document


def main() -> int:
    """
    Entry point for the script.

    Parses command-line arguments and converts CSV from stdin to HTML.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Convert CSV to HTML using tabulate.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: cat data.csv | python csv2html.py -d ',' -o output.html"
    )
    parser.add_argument(
        "-d", "--delimiter",
        default=",",
        help="Specify the CSV delimiter (default: ',')"
    )
    parser.add_argument(
        "-q", "--quote-char",
        default='"',
        help="Specify the quote character (default: '\"')"
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
    parser.add_argument(
        "--skip-empty-lines",
        action="store_true",
        default=True,
        help="Skip empty lines in CSV parsing (default: True)"
    )
    parser.add_argument(
        "--no-skip-empty-lines",
        action="store_false",
        dest="skip_empty_lines",
        help="Do not skip empty lines in CSV parsing"
    )
    parser.add_argument(
        "--trim-whitespace",
        action="store_true",
        default=True,
        help="Trim whitespace from all cells (default: True)"
    )
    parser.add_argument(
        "--no-trim-whitespace",
        action="store_false",
        dest="trim_whitespace",
        help="Do not trim whitespace from cells"
    )
    parser.add_argument(
        "--strict-columns",
        action="store_true",
        help="Strict column validation (fail on inconsistent column counts)"
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        return 1

    # Validate delimiter
    if not args.delimiter:
        print("Error: Delimiter cannot be empty", file=sys.stderr)
        return 1

    # Validate quote character
    if len(args.quote_char) != 1:
        print("Error: Quote character must be a single character", file=sys.stderr)
        return 1

    # Check for input data
    if sys.stdin.isatty():
        print("Error: No input provided. Please pipe CSV data to stdin.", file=sys.stderr)
        print("Example: cat data.csv | python csv2html.py", file=sys.stderr)
        return 1

    try:
        input_data: str = sys.stdin.read()
        if not input_data:
            print("Error: No data received from stdin", file=sys.stderr)
            return 1

        html_document: str = csv_to_html(
            input_data,
            args.delimiter,
            args.suppress,
            args.skip_empty_lines,
            args.quote_char,
            args.trim_whitespace
        )

        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as output_file:
                    output_file.write(html_document)
                print(f"HTML document written to {args.output}")
            except PermissionError:
                print(f"Error: Permission denied writing to {args.output}", file=sys.stderr)
                return 1
            except FileNotFoundError:
                print(f"Error: Directory not found for output path {args.output}", file=sys.stderr)
                return 1
            except OSError as e:
                print(f"Error: Unable to write to {args.output}: {e}", file=sys.stderr)
                return 1
        else:
            try:
                print(html_document)
            except BrokenPipeError:
                pass

        return 0

    except ValueError as e:
        print(f"CSV parsing error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation interrupted by user", file=sys.stderr)
        return 1
    except MemoryError:
        print("Error: Not enough memory to process the CSV data", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())