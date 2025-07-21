
#! /usr/bin/env python3

import sys
import json
import argparse
from typing import Any, List, Dict
from datetime import datetime
import plotext as plt

DATE_FORMAT: str = "%Y-%m-%d"  # Default date format for parsing

def parse_json_data(data_str: str) -> List[Dict[str, Any]]:
    """
    Parse JSON string into a list of dictionaries.
    """
    try:
        data: Any = json.loads(data_str)
        if isinstance(data, dict):
            return [data]
        if not isinstance(data, list):
            raise ValueError("JSON data must be a list of objects or a single object.")
        return data
    except Exception as e:
        print(f"Error: Invalid JSON data. {e}", file=sys.stderr)
        sys.exit(1)

def get_data_input(args: argparse.Namespace) -> List[Dict[str, Any]]:
    """
    Retrieve and parse the data input for the chart from --data or stdin.
    """
    if args.data:
        return parse_json_data(args.data)
    if not sys.stdin.isatty():
        input_str: str = sys.stdin.read().strip()
        if input_str:
            return parse_json_data(input_str)
    print("Error: No data provided via --data or stdin.", file=sys.stderr)
    sys.exit(1)

def validate_chart_arguments(args: argparse.Namespace):
    """
    Validate required arguments for plotting.
    """
    if not args.xkey or not args.ykey:
        print("Error: --xkey and --ykey are required options.", file=sys.stderr)
        sys.exit(1)

def show_help():
    print(
        """
Usage: chart.py [options]
Options:
  -d, --data      Provide data for the chart in JSON format
  -x, --xkey      Specify the key for the x-axis (date or category)
  -y, --ykey      Specify the key for the y-axis (value)
  --date-format   Specify the date format for the x-axis (default: %Y-%m-%d)
  -t, --title     Set the chart title
  --xlabel        Set the x-axis label
  --ylabel        Set the y-axis label
  --theme         Set the plot theme (default: dark)
  -h, --help      Show this help message
        """
    )

def plot_time_series(data: List[Dict[str, Any]], xkey: str, ykey: str, date_format: str, title: str, xlabel: str, ylabel: str, theme: str):
    """
    Plot a time series chart using plotext.
    """
    try:
        date_y_pairs = []
        for row in data:
            x_val = row.get(xkey)
            y_val = row.get(ykey)
            if x_val is None or y_val is None:
                continue
            try:
                dt = datetime.strptime(str(x_val), date_format)
                date_y_pairs.append((dt, float(y_val)))
            except Exception as e:
                print(f"Warning: Skipping row with invalid date '{x_val}': {e}", file=sys.stderr)
                continue
        if not date_y_pairs:
            print("Error: No valid data points for plotting.", file=sys.stderr)
            sys.exit(1)
        # Sort by date
        date_y_pairs.sort(key=lambda pair: pair[0])
        x = [dt.strftime(date_format) for dt, _ in date_y_pairs]
        y = [val for _, val in date_y_pairs]
        plt.clear_figure()
        # plotext expects date_form like 'd-b-y' for '%d-%b-%y'
        # Remove all '%' and lowercase the format letters
        date_form_str = date_format.replace('%', '').replace('Y', 'y').replace('m', 'm').replace('d', 'd').replace('b', 'b')
        try:
            plt.date_form(date_form_str)
        except Exception as e:
            print(f"Warning: Could not set date_form '{date_form_str}': {e}", file=sys.stderr)
        plt.plot(x, y)
        if title:
            plt.title(title)
        plt.theme(theme or "dark")
        plt.xlabel(xlabel or xkey)
        plt.ylabel(ylabel or ykey)
        plt.show()
    except Exception as e:
        print(f"Error: Failed to plot time series. {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", "--data", type=str, help="JSON data string for the chart")
    parser.add_argument("-x", "--xkey", type=str, help="Key for the x-axis (date or category)")
    parser.add_argument("-y", "--ykey", type=str, help="Key for the y-axis (value)")
    parser.add_argument("--date-format", type=str, default=DATE_FORMAT, help="Date format for x-axis (default: %%Y-%%m-%%d)")
    parser.add_argument("-t", "--title", type=str, default="", help="Chart title")
    parser.add_argument("--xlabel", type=str, default="", help="X-axis label")
    parser.add_argument("--ylabel", type=str, default="", help="Y-axis label")
    parser.add_argument("--theme", type=str, default="dark", help="Plot theme (default: dark)")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message")
    args = parser.parse_args()

    if args.help:
        show_help()
        sys.exit(0)

    validate_chart_arguments(args)
    data = get_data_input(args)
    plot_time_series(
        data,
        xkey=args.xkey,
        ykey=args.ykey,
        date_format=args.date_format,
        title=args.title,
        xlabel=args.xlabel,
        ylabel=args.ylabel,
        theme=args.theme,
    )

if __name__ == "__main__":
    main()