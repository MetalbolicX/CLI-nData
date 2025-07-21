#! /usr/bin/env python3

import sys
import json
import argparse
from typing import Any, List, Dict
from datetime import datetime
import plotext as plt

SUCCESS_EXIT_CODE: int = 0
ERROR_EXIT_CODE: int = 1
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
        return []

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
    return []

def validate_chart_arguments(args: argparse.Namespace) -> bool:
    """
    Validate required arguments for plotting.
    """
    if not args.xkey or not args.ykey:
        print("Error: --xkey and --ykey are required options.", file=sys.stderr)
        return False
    return True

def show_help() -> None:
    print(
        """
Usage: chart.py [options]
Options:
    -b, --bins              Number of bins for histogram (default: 10)
    -d, --data              Provide data for the chart in JSON format
    -df, --date-format      Specify the date format for the x-axis (default: %Y-%m-%d)
    -h, --help              Show this help message
    -T, --title             Set the chart title
    -t, --type              Specify the type of chart (time_series, histogram)
    -th, --theme            Set the plot theme (default: dark)
    -x, --xkey              Specify the key for the x-axis (date or category)
    -xlb, --xlabel          Set the x-axis label
    -y, --ykey              Specify the key for the y-axis (value)
    -ylb, --ylabel          Set the y-axis label
        """
    )

def plot_histogram(
    data: List[Dict[str, Any]],
    ykey: str,
    bins: int,
    title: str,
    xlabel: str,
    ylabel: str,
    theme: str
) -> int:
    """
    Plot a histogram using plotext.
    """
    try:
        values: List[float] = []
        for row in data:
            y_val = row.get(ykey)
            if y_val is not None:
                try:
                    values.append(float(y_val))
                except Exception:
                    continue
        if not values:
            print("Error: No valid data points for histogram.", file=sys.stderr)
            return ERROR_EXIT_CODE
        plt.clear_figure()
        plt.hist(values, bins=bins)
        if title:
            plt.title(title)
        plt.theme(theme or "dark")
        plt.xlabel(xlabel or ykey)
        plt.ylabel(ylabel or "Frequency")
        plt.show()
        return SUCCESS_EXIT_CODE
    except Exception as e:
        print(f"Error: Failed to plot histogram. {e}", file=sys.stderr)
        return ERROR_EXIT_CODE

def plot_time_series(
    data: List[Dict[str, Any]],
    xkey: str,
    ykey: str,
    date_format: str,
    title: str,
    xlabel: str,
    ylabel: str,
    theme: str
) -> int:
    """
    Plot a time series chart using plotext.
    """
    try:
        date_y_pairs: List[Any] = []
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
            return ERROR_EXIT_CODE
        date_y_pairs.sort(key=lambda pair: pair[0])
        x: List[str] = [dt.strftime(date_format) for dt, _ in date_y_pairs]
        y: List[float] = [val for _, val in date_y_pairs]
        plt.clear_figure()
        date_form_str: str = date_format.replace('%', '').replace('Y', 'y').replace('m', 'm').replace('d', 'd').replace('b', 'b')
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
        return SUCCESS_EXIT_CODE
    except Exception as e:
        print(f"Error: Failed to plot time series. {e}", file=sys.stderr)
        return ERROR_EXIT_CODE

def main() -> int:
    try:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-d", "--data", type=str, help="JSON data string for the chart")
        parser.add_argument("-x", "--xkey", type=str, help="Key for the x-axis (date or category)")
        parser.add_argument("-y", "--ykey", type=str, help="Key for the y-axis (value)")
        parser.add_argument("-df", "--date-format", type=str, default=DATE_FORMAT, help="Date format for x-axis (default: %%Y-%%m-%%d)")
        parser.add_argument("-t", "--type", type=str, default="time_series", help="Type of chart (time_series, histogram)")
        parser.add_argument("-T", "--title", type=str, default="", help="Chart title")
        parser.add_argument("-xlb", "--xlabel", type=str, default="", help="X-axis label")
        parser.add_argument("-ylb", "--ylabel", type=str, default="", help="Y-axis label")
        parser.add_argument("-th", "--theme", type=str, default="dark", help="Plot theme (default: dark)")
        parser.add_argument("-b", "--bins", type=int, default=10, help="Number of bins for histogram (default: 10)")
        parser.add_argument("-h", "--help", action="store_true", help="Show help message")
        args = parser.parse_args()

        if args.help:
            show_help()
            return SUCCESS_EXIT_CODE

        data: List[Dict[str, Any]] = get_data_input(args)
        if not data:
            return ERROR_EXIT_CODE

        chart_type: str = args.type.lower()
        if chart_type == "time_series":
            if not validate_chart_arguments(args):
                return ERROR_EXIT_CODE
            return plot_time_series(
                data,
                xkey=args.xkey,
                ykey=args.ykey,
                date_format=args.date_format,
                title=args.title,
                xlabel=args.xlabel,
                ylabel=args.ylabel,
                theme=args.theme,
            )
        elif chart_type == "histogram":
            if not args.ykey:
                print("Error: --ykey is required for histogram.", file=sys.stderr)
                return ERROR_EXIT_CODE
            return plot_histogram(
                data,
                ykey=args.ykey,
                bins=args.bins,
                title=args.title,
                xlabel=args.xlabel,
                ylabel=args.ylabel,
                theme=args.theme,
            )
        else:
            print(f"Error: Unknown chart type '{args.type}'. Supported types: time_series, histogram.", file=sys.stderr)
            return ERROR_EXIT_CODE

    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return ERROR_EXIT_CODE
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return ERROR_EXIT_CODE

if __name__ == "__main__":
    sys.exit(main())