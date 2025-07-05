#!/usr/bin/env python3

"""
This script generates various types of plots (line, scatter, bar, time series) using termplotlib or gnuplot.

Example usage:
$ echo '[{"hours": 0, "sales": 0}, {"hours": 1, "sales": 2}]' | python3 plot.py --type line --xkey "hours" --ykey "sales" --title "Sales Over Time"

Dependencies:
- termplotlib
- gnuplot (for scatter, vertical bar, and line time series charts)

Author: José Martínez Santana
"""

import argparse
import json
import sys
from typing import List, Dict, Union
import termplotlib as tpl
import subprocess

# Define type annotations for data points
LineScatterCoordinates = List[Dict[str, Union[int, float]]]
BarInfo = List[Dict[str, Union[str, int, float]]]

def plot_with_gnuplot(data: LineScatterCoordinates, xkey: str, ykey: str, title: str, plot_type: str) -> None:
    """
    Plots using gnuplot for scatter, vertical bar, and line time series charts.

    Args:
        data (LineScatterCoordinates): List of dictionaries containing data points.
        xkey (str): Key for x-axis values.
        ykey (str): Key for y-axis values.
        title (str): Title of the plot.
        plot_type (str): Type of plot (scatter, vertical_bar, line_time_series).

    Returns:
        None
    """
    x = [str(point[xkey]) for point in data]
    y = [str(point[ykey]) for point in data]

    # Prepare data for gnuplot
    gnuplot_data = "\n".join(f"{i + 1} {y[i]} \"{x[i]}\"" for i in range(len(x)))

    # Determine gnuplot command based on plot type
    gnuplot_command = [
        "gnuplot",
        "-e",
        f"set term dumb; set title '{title}'; set xtics rotate by -45; plot '-' using 1:2:xticlabels(3) with {plot_type}"
    ]

    # Execute gnuplot
    process = subprocess.Popen(gnuplot_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=gnuplot_data.encode())

    if process.returncode != 0:
        sys.stderr.write(f"Error: gnuplot failed with error:\n{stderr.decode()}\n")
        sys.exit(1)

    # Print the plot to the terminal
    sys.stdout.write(stdout.decode())

def plot_line(coordinates: LineScatterCoordinates, xkey: str, ykey: str, title: str) -> None:
    x = [coordinate[xkey] for coordinate in coordinates]
    y = [coordinate[ykey] for coordinate in coordinates]
    fig = tpl.figure()
    fig.plot(x, y, label=title)
    fig.show()

def plot_horizontal_bar(dataset: BarInfo, xkey: str, ykey: str) -> None:
    labels = [datum[xkey] for datum in dataset]
    values = [datum[ykey] for datum in dataset]
    fig = tpl.figure()
    fig.barh(values, labels)
    fig.show()

def validate_json(data: str) -> Union[LineScatterCoordinates, BarInfo]:
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.stderr.write("Error: The provided data is not valid JSON.\n")
        sys.exit(1)

def main() -> int:
    parser = argparse.ArgumentParser(description="Plot charts using termplotlib or gnuplot.")
    parser.add_argument("--type", required=True, choices=["line", "scatter", "vertical_bar", "horizontal_bar", "time_series"], help="Type of plot")
    parser.add_argument("--data", nargs="?", type=argparse.FileType("r"), default=sys.stdin, help="Input data in JSON format")
    parser.add_argument("--title", default="", help="Title of the chart")
    parser.add_argument("--xkey", default="x", help="Key for X-axis values in JSON data")
    parser.add_argument("--ykey", default="y", help="Key for Y-axis values in JSON data")

    args = parser.parse_args()

    # Validate JSON input
    data = validate_json(args.data.read())

    # Strategy pattern using a dictionary to map plot types to functions
    plot_functions = {
        "line": lambda: plot_line(data, args.xkey, args.ykey, args.title),
        "scatter": lambda: plot_with_gnuplot(data, args.xkey, args.ykey, args.title, "points"),
        "vertical_bar": lambda: plot_with_gnuplot(data, args.xkey, args.ykey, args.title, "boxes"),
        "time_series": lambda: plot_with_gnuplot(data, args.xkey, args.ykey, args.title, "lines"),
        "horizontal_bar": lambda: plot_horizontal_bar(data, args.xkey, args.ykey)
    }

    # Execute the appropriate plotting function
    if args.type in plot_functions:
        plot_functions[args.type]()
    else:
        sys.stderr.write(f"Error: Plot type '{args.type}' is not supported.\n")
        sys.exit(1)

    return 0

if __name__ == "__main__":
    sys.exit(main())