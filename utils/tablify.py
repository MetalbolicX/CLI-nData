#!/usr/bin/env python3
"""
CLI wrapper for the tabulate package. Reads tabular data from a file or stdin and prints a formatted table.
"""
import sys
import argparse
from tabulate import tabulate

SUCCESS_EXIT_CODE: int = 0
ERROR_EXIT_CODE: int = 1

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for the tablify script."""
    parser = argparse.ArgumentParser(
        description="Format tabular data using the tabulate package.",
        add_help=False
    )
    parser.add_argument("file", nargs="?", default="-", help="a filename of the file with tabular data; if '-' or missing, read data from stdin.")
    parser.add_argument("-H", "--header", action="store_true", help="use the first row of data as a table header")
    parser.add_argument("-o", "--output", metavar="FILE", help="print table to FILE (default: stdout)")
    parser.add_argument("-s", "--sep", metavar="REGEXP", default=None, help="use a custom column separator (default: whitespace)")
    parser.add_argument("-F", "--float", dest="float_fmt", metavar="FPFMT", default="g", help="floating point number format (default: g)")
    parser.add_argument("-I", "--int", dest="int_fmt", metavar="INTFMT", default="", help="integer point number format (default: '')")
    parser.add_argument("-f", "--format", dest="table_format", metavar="FMT", default="simple", help="set output table format")
    parser.add_argument("-h", "--help", action="store_true", help="show this message")
    return parser.parse_args()

def read_data(file: str, sep: str | None) -> list[list[str]]:
    """Read tabular data from a file or stdin.

    Args:
        file (str): The filename to read data from, or '-' to read from stdin.
        sep (str | None): A regular expression to use as a custom column separator.

    Returns:
        list[list[str]]: The tabular data as a list of rows, each row being a list of strings.
    """
    import re
    try:
        if file == "-":
            if not sys.stdin.isatty():
                lines = sys.stdin.read().splitlines()
            else:
                print("Error: No input provided via stdin or file.", file=sys.stderr)
                return []
        else:
            with open(file, "r") as f:
                lines = f.read().splitlines()
        if not lines:
            return []
        if sep:
            splitter = re.compile(sep)
            return [splitter.split(line) for line in lines]
        return [line.split() for line in lines]
    except Exception as e:
        print(f"Error: Failed to read data. {e}", file=sys.stderr)
        return []

def show_help() -> None:
    """Display the help message for the tablify script."""
    print(
        """
Usage: tablify.py [options] [FILE]
Options:
    -H, --header              use the first row of data as a table header
    -o FILE, --output FILE    print table to FILE (default: stdout)
    -s REGEXP, --sep REGEXP   use a custom column separator (default: whitespace)
    -F FPFMT, --float FPFMT   floating point number format (default: g)
    -I INTFMT, --int INTFMT   integer point number format (default: '')
    -f FMT, --format FMT      set output table format (default: simple)
    -h, --help                show this message
    FILE                      a filename of the file with tabular data; if '-' or missing, read data from stdin.
        """
    )

def main() -> int:
    """Main function to parse arguments, read data, and print the formatted table."""
    try:
        args = parse_arguments()
        if args.help:
            show_help()
            return SUCCESS_EXIT_CODE
        data = read_data(args.file, args.sep)
        if not data:
            return ERROR_EXIT_CODE
        if args.header:
            headers = data[0]
            rows = data[1:]
            table = tabulate(
                rows,
                headers=headers,
                tablefmt=args.table_format,
                floatfmt=args.float_fmt,
                intfmt=args.int_fmt
            )
        else:
            table = tabulate(
                data,
                tablefmt=args.table_format,
                floatfmt=args.float_fmt,
                intfmt=args.int_fmt
            )
        if args.output:
            try:
                with open(args.output, "w") as f:
                    f.write(table + "\n")
            except Exception as e:
                print(f"Error: Failed to write output file. {e}", file=sys.stderr)
                return ERROR_EXIT_CODE
        else:
            print(table)
        return SUCCESS_EXIT_CODE
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return ERROR_EXIT_CODE
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return ERROR_EXIT_CODE


if __name__ == "__main__":
    sys.exit(main())
