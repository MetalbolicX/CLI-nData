# API Reference

This page documents the core scripts of the cli-ndata package.

## `body`

## `cols`

## `dseq`

This command generates a sequence of dates relative to a start day. It allows you to specify the starting date, increment, and format for the output dates. The script is powered by the `date` command and supports flexible date formatting and offsets.

### Usage

```sh
dseq [OPTIONS] LAST
dseq [OPTIONS] FIRST LAST
dseq [OPTIONS] FIRST INCREMENT LAST
```

### Arguments

- `LAST`: Generates dates from `FIRST` (default `0` for today) up to `LAST`. If only `LAST` is given, it implies `FIRST=1` and `INCREMENT=1`.
- `FIRST`: The starting offset in days from the base date.
- `INCREMENT`: The step size in days for the sequence.

### Options

- `-f, --format <format_string>`: Specify the output date format (e.g., `%Y-%m-%d`, `%A, %B %d, %Y`). Uses `date` command format codes. Default: `+%F` (YYYY-MM-DD).
- `-s, --start-date <date_string>`: Specify the base date to start from (e.g., `2023-01-01`, `tomorrow`, `yesterday`). Default: today. This affects the `0 day` offset.
- `-h, --help`: Display this help message and exit.

### Examples

#### Generate Tomorrow's Date

```sh
dseq 1
```
Output: Tomorrow's date (default: start=today, first=1, inc=1, last=1).

#### Generate Today's Date

```sh
dseq 0 0
```
Output: Today's date (start=today, first=0, last=0).

#### Generate Next 7 Days

```sh
dseq 7
```
Output: Dates for the next 7 days (start=today, first=1, inc=1, last=7).

#### Generate a Range of Dates

```sh
dseq -2 0
```
Output: Dates from the day before yesterday to today (start=today, first=-2, inc=1, last=0).

#### Generate Weekly Dates for a Year

```sh
dseq 1 7 365
```
Output: Dates starting tomorrow and then every week for a year (start=today, first=1, inc=7, last=365).

#### Custom Date Format

```sh
dseq -f "%Y/%m/%d %a" 0 2
```
Output: Today, tomorrow, and the day after tomorrow in `YYYY/MM/DD Day` format.

#### Start from a Specific Date

```sh
dseq -s "2024-12-25" 0 2
```
Output: Dates starting from December 25, 2024.

#### Generate Dates Relative to a Specific Day

```sh
dseq -s "last friday" -1 0
```
Output: Dates for last Friday and Saturday.

## `dumbplot`

This command is used to plot data in ASCII characters by using `gnuplot` dependency. It can handle categorical, numerical and time series data.

### Usage

```sh
dumbplot [OPTIONS]
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
curl 'https://example.com' -s | scrape -e 'a' -a 'href'
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

## `servedir`

This command is used to serve a static website from a specified working directory. It uses Python's built-in HTTP server capabilities to serve files over HTTP.

### Usage

```sh
servedir [PORT] [DIR]
```

### Arguments

- `PORT`: The port number to serve the website on. Default is `8000`. If not specified, it will use the default port.
- `DIR`: The directory to serve files from. Default is the current working directory. If not specified, it will use the current directory.

### Examples

#### Serve Current Directory on Default Port

```sh
servedir
```

Output: Serves the current directory on port `8000`.

#### Serve in another Port

```sh
servedir 8080
```

Output: Serves the current directory on port `8080`.

#### Serve a Specific Directory

```sh
servedir 8080 /path/to/directory
```

Output: Serves the specified directory on port `8080`.

?> When another directory is specifies. The port needs to be specified as well, otherwise, it will cause an error.

## `trim`

This command trims the output to a specified height (number of lines) and width (number of characters per line). It is useful for limiting the size of terminal output, especially when working with large datasets or long lines of text. Tabs are expanded to spaces before trimming.

### Usage

```sh
trim [height] [width]
```

### Arguments

- `height`: The maximum number of lines to display. Default: `10`. Pass a negative number to disable height trimming.
- `width`: The maximum number of characters per line. Default: terminal width. Pass a negative number to disable width trimming.

### Features

- **Height Trimming**: Limits the number of lines displayed. If the output exceeds the specified height, a summary of the remaining lines is shown.
- **Width Trimming**: Limits the number of characters per line. Lines longer than the specified width are truncated and appended with `…`.
- **Tabs Expansion**: Tabs are converted to spaces before trimming.
- **Fallback Width**: If terminal width cannot be determined, defaults to `80` characters.

### Examples

#### Trim Output to Default Height and Width

```sh
seq 100 | trim
```

Output: Displays the first 10 lines, trimmed to the terminal width.

#### Trim Output to a Specific Height

```sh
seq 100 | trim 20
```

Output: Displays the first 20 lines, trimmed to the terminal width.

#### Trim Output to a Specific Height and Width

```sh
seq 100 | trim 20 40
```

Output: Displays the first 20 lines, with each line trimmed to 40 characters.

#### Disable Height Trimming

```sh
seq 100 | trim -1 40
```

Output: Displays all lines, with each line trimmed to 40 characters.


#### Disable Width Trimming

```sh
seq 100 | trim 20 -1
```

Output: Displays the first 20 lines, without trimming the width.
