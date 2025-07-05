#!/usr/bin/env python3

"""
This script generates various types of plots (line, scatter, bar, time series) using termplotlib.

Example usage:
$ python plot.py --type line --data '[{"x": 0, "y": 0}, {"x": 1, "y": 2}]' --title "Line Chart"

Dependencies:
- termplotlib

Author: José Martínez Santana
"""

import argparse
import json
import sys
from typing import List, Dict, Union
import termplotlib as tpl

# Define type annotations for data points
LineScatterCoordinates = List[Dict[str, Union[int, float]]]
BarInfo = List[Dict[str, Union[str, int, float]]]

def plot_line(coordinates: LineScatterCoordinates, title: str, xlabel: str, ylabel: str) -> None:
    x = [coordinate['x'] for coordinate in coordinates]
    y = [coordinate['y'] for coordinate in coordinates]
    fig = tpl.figure()
    fig.plot(x, y, label=title)
    fig.show()

def plot_scatter(coordinates: LineScatterCoordinates, title: str, xlabel: str, ylabel: str) -> None:
    x = [coordinate['x'] for coordinate in coordinates]
    y = [coordinate['y'] for coordinate in coordinates]
    fig = tpl.figure()
    fig.scatter(x, y, label=title)
    fig.show()

def plot_bar(dataset: BarInfo, title: str, xlabel: str, ylabel: str, orientation: str = 'vertical') -> None:
    labels = [datum['label'] for datum in dataset]
    values = [datum['value'] for datum in dataset]
    fig = tpl.figure()
    if orientation == 'vertical':
        fig.bar(values, labels, label=title)
    else:
        fig.barh(values, labels, label=title)
    fig.show()

def plot_time_series(data: LineScatterCoordinates, title: str, xlabel: str, ylabel: str) -> None:
    x = [point['x'] for point in data]
    y = [point['y'] for point in data]
    fig = tpl.figure()
    fig.plot(x, y, label=title)
    fig.show()

def validate_json(data: str) -> Union[LineScatterCoordinates, BarInfo]:
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.stderr.write("Error: The provided data is not valid JSON.\n")
        sys.exit(1)

def main() -> int:
    parser = argparse.ArgumentParser(description="Plot charts using termplotlib.")
    parser.add_argument("--type", required=True, choices=["line", "scatter", "bar", "time_series"], help="Type of plot")
    parser.add_argument("--data", required=True, help="Input data in JSON format")
    parser.add_argument("--title", default="", help="Title of the chart")
    parser.add_argument("--xlabel", default="", help="Label for the X-axis")
    parser.add_argument("--ylabel", default="", help="Label for the Y-axis")
    parser.add_argument("--orientation", choices=["vertical", "horizontal"], default="vertical", help="Bar chart orientation")

    args = parser.parse_args()

    # Validate JSON input
    data = validate_json(args.data)

    # Strategy pattern using a dictionary to map plot types to functions
    plot_functions = {
        "line": lambda: plot_line(data, args.title, args.xlabel, args.ylabel),
        "scatter": lambda: plot_scatter(data, args.title, args.xlabel, args.ylabel),
        "bar": lambda: plot_bar(data, args.title, args.xlabel, args.ylabel, args.orientation),
        "time_series": lambda: plot_time_series(data, args.title, args.xlabel, args.ylabel),
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