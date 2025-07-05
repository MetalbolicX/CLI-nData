#!/usr/bin/env python3
import csv
import argparse
import os
import html

def is_header_row(row: list[str]) -> bool:
    """
    Determine if a row from the CSV file is a header row.

    A header row is identified as a row containing non-numeric values.
    This function checks if all values in the row are non-empty and non-numeric.

    Args:
        row (list[str]): A list of strings representing a row from the CSV file.

    Returns:
        bool: True if the row is a header row, False otherwise.
    """
    for value in row:
        if value.strip() == "" or value.isnumeric():
            return False
    return True

def generate_default_headers(count: int) -> list[str]:
    """
    Generate default column headers for a CSV file.

    If the CSV file does not contain headers, this function generates
    default headers in the format 'Column1', 'Column2', ..., 'ColumnN'.

    Args:
        count (int): The number of columns in the CSV file.

    Returns:
        list[str]: A list of default column headers.
    """
    return [f"Column{i+1}" for i in range(count)]

def csv_2_html(input_file: str, delimiter: str, suppress: bool) -> None:
    """
    Convert a CSV file to an HTML table and print it to the console.

    This function reads a CSV file, processes its contents, and generates
    an HTML table. If the CSV file does not contain headers, default headers
    are generated. Rows can be suppressed from being printed using the suppress flag.

    Args:
        input_file (str): Path to the input CSV file.
        delimiter (str): The delimiter used in the CSV file (e.g., ',' or ';').
        suppress (bool): If True, suppress printing rows to the console.

    Returns:
        None
    """
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        return

    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)

        try:
            headers = next(reader)
        except StopIteration:
            print("Error: CSV file is empty.")
            return

        # Check if headers are valid
        if not is_header_row(headers):
            headers = generate_default_headers(len(headers))
            print("Warning: Missing headers in CSV file. Default headers generated.")

        # Start HTML generation
        print("<!DOCTYPE html>")
        print("<html>")
        print("<head>")
        print("<title>CSV to HTML</title>")
        print("</head>")
        print("<body>")
        print("<table border=\"1\">")
        print("<thead>")
        print("<tr>")
        for header in headers:
            print(f"<th>{html.escape(header)}</th>")
        print("</tr>")
        print("</thead>")
        print("<tbody>")

        # Process rows one by one
        for row in reader:
            if not suppress:
                print("<tr>")
                for value in row:
                    print(f"<td>{html.escape(value)}</td>")
                print("</tr>")

        print("</tbody>")
        print("</table>")
        print("</body>")
        print("</html>")

if __name__ == "__main__":
    """
    Entry point for the script.

    Parses command-line arguments and calls the csv_to_html function
    to convert the specified CSV file to HTML.
    """
    parser = argparse.ArgumentParser(description="Convert CSV to HTML.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("-d", "--delimiter", default=",", help="Specify the CSV delimiter (default: ',').")
    parser.add_argument("-s", "--suppress", action="store_true", help="Suppress printing each row to the screen.")
    args = parser.parse_args()

    input_file: str = args.input_file
    delimiter: str = args.delimiter
    suppress: bool = args.suppress

    csv_2_html(input_file, delimiter, suppress)