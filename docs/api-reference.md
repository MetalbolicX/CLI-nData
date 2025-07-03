# API Reference

This page documents the core scripts of the cli-ndata package.

## `body`

## `cols`

## `dseq`

## `dumbplot`

This command is used to plot data in ASCII characters by using `gnuplot` dependency. It can handle categorical, numerical and time series data.

### Usage

```sh
dumbplot [options]
```

### Options

- `-a`, Treat x-coordinates as categorical data for plotting.
- `-b`, Use vertical boxes for bar-like plots (implies `-a`).
- `-w`, Specifies the terminal width (by default is the terminal width).
- `-v`, Specifies the terminal height (by default is 50% the terminal height).
- `-h`, Display help message.

### Examples

#### Bar Chart

Requires the `-b` flag.

```sh
echo -e "A,10\nB,20\nC,15\nD,25\nE,30" | dumbplot -b
```

#### Line Chart (with numerical data)

Automatically connects points with lines for numerical data.

```sh
echo -e "1,10\n2,20\n3,15\n4,25\n5,30" | dumbplot
```

#### Time Series Plot

Dates are treated as categorical labels using `xticlabels(1)`.

```sh
echo -e "2025-07-01,10\n2025-07-02,20\n2025-07-03,15" | dumbplot
```

#### Scatter Plot

Default behavior without any flags.

```sh
echo -e "1,10\n2,20\n3,15\n4,25\n5,30" | dumbplot
```

## `header`

## `scrape`

This command is used to scrape data from a webpage using **CSS selectors** or **XPath**. It allows you to extract specific sections from HTML document. This script requires **Python 3** and it is powered by `cssselect` and `lxml` libraries. Automatically starts a virtual environment if not already activated and at the end deactivates it.

### Usage

```sh
scrape <html_text> [options]
```

### Options



## `trim`