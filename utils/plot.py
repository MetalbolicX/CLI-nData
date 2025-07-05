#!/usr/bin/env python3

"""
This script generates various types of plots (line, scatter, bar, time series) using termplotlib.

Example usage:
$ python plot.py --type line --data '[{"hours": 0, "sales": 0}, {"hours": 1, "sales": 2}]' --xkey "hours" --ykey "sales" --title "Sales Over Time"

Dependencies:
- termplotlib

Author: José Martínez Santana
"""

import argparse
import json
import sys
from typing import Union
import termplotlib as tpl

# Define type annotations for data points
NumericalCoordinates = list[dict[str, Union[int, float]]]
CategoricalCoordinates = list[dict[str, Union[int, float]]]

def plot_line(coordinates: NumericalCoordinates, xkey: str, ykey: str, title: str) -> None:
    """
    Plots a line graph using the provided coordinates and axis labels.

    Args:
        coordinates (NumericalCoordinates): A list of dictionaries containing data points for plotting.
        xkey (str): The key to extract x-axis values from each coordinate.
        ykey (str): The key to extract y-axis values from each coordinate.
        title (str): The title of the plot and the label for the line.

    Returns:
        None
    """
    x = [coordinate[xkey] for coordinate in coordinates]
    y = [coordinate[ykey] for coordinate in coordinates]
    fig = tpl.figure()
    fig.plot(x, y, label=title)
    fig.show()

def plot_horizontal_bar(dataset: CategoricalCoordinates, xkey: str, ykey: str) -> None:
    labels = [datum[xkey] for datum in dataset]
    values = [datum[ykey] for datum in dataset]
    fig = tpl.figure()
    fig.barh(values, labels)
    fig.show()

def validate_json(data: str) -> Union[NumericalCoordinates, CategoricalCoordinates]:
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.stderr.write("Error: The provided data is not valid JSON.\n")
        sys.exit(1)

def main() -> int:
    parser = argparse.ArgumentParser(description="Plot charts using termplotlib.")
    parser.add_argument("--type", required=True, choices=["line", "scatter", "horizontal_bar", "time_series"], help="Type of plot")
    parser.add_argument("--data", required=True, help="Input data in JSON format")
    parser.add_argument("--title", default="", help="Title of the chart")
    parser.add_argument("--xkey", default="x", help="Key for X-axis values in JSON data")
    parser.add_argument("--ykey", default="y", help="Key for Y-axis values in JSON data")

    args = parser.parse_args()

    # Validate JSON input
    dataset = validate_json(args.data)

    # Using a dictionary to map plot types to functions
    plot_functions = {
        "line": lambda: plot_line(dataset, args.xkey, args.ykey, args.title),
        "horizontal_bar": lambda: plot_horizontal_bar(dataset, args.xkey, args.ykey),
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