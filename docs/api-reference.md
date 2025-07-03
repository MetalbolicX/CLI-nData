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

- `-a, --attribute`: Extract a specific attribute from the HTML tag (e.g., `href`, `src`).
- `-b, --include_body_tags`: Enclose the output with `<html>` and `<body>` tags.
- `-e, --selectors`: Specify XPath queries or CSS3 selectors to extract elements. Can be used multiple times.
- `-f, --input_file`: Specify a file to read the HTML input from instead of `stdin`.
- `-x, --check_existence`: Exit with code `0` if elements exist, otherwise exit with code `1`.
- `-r, --raw_input`: Do not parse the HTML before feeding it to `etree`. Useful for escaping CData.

### Examples

#### Extract Links from a Webpage
Extract all links (`<a>` tags) from a webpage:
```sh
curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s | scrape -e 'a' -a 'href'
```

#### Extract Table Data Using CSS Selectors
Extract bold text inside table cells from a Wikipedia page:
```sh
curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s | scrape -e 'table.wikitable > tbody > tr > td > b > a'
```

#### Extract Specific Attributes
Extract the `src` attribute of all `<img>` tags:
```sh
curl 'https://example.com' -s | scrape -e 'img' -a 'src'
```

#### Check Existence of Elements
Check if a specific element exists on a webpage:
```sh
curl 'https://example.com' -s | scrape -e 'div#main-content' -x
```

#### Process Raw HTML Input
Process raw HTML without parsing:
```sh
cat raw_html_file.html | scrape -r -e '//div[@class="content"]'
```

#### Include HTML and BODY Tags in Output
Wrap the output with `<html>` and `<body>` tags:
```sh
curl 'https://example.com' -s | scrape -e 'p' -b
```

#### Read HTML from a File
Read HTML input from a file instead of `stdin`:
```sh
scrape -f input.html -e 'h1'
```

?>
**CSS Selectors**: If a selector is provided, it is automatically converted to XPath using `cssselect`.
**XPath Queries**: XPath expressions can be used directly by prefixing them with `//`.

### Usage



## `trim`