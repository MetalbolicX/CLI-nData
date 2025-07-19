# API Reference

This page documents the core scripts of the cli-ndata package.

## `body`

This command applies a given shell command to all lines except the first (header) line of input. It is useful for processing tabular data, CSV files, or any structured text where the header should be preserved and the body transformed. For multi-line headers, chain `body` multiple times. The command reads from standard input and outputs the header unchanged, then pipes the remaining lines to the specified command.

**Dependency:** Bash (no external dependencies)

### Usage

```sh
body <command> [args...]
```

### Arguments

- `<command> [args...]`: The shell command to apply to the body (all lines except the first).

### Features

- Preserves the first line (header) and applies the given command to the rest.
- Can be chained to skip multiple header lines.
- Works with any shell command that reads from stdin.

### Examples

#### Sort the body numerically in reverse order

```sh
seq 10 | header -a 'values' | body sort -nr
```

#### Skip a multi-line header (chain body)

```sh
seq 10 | header -a 'multi\nline\nheader' | body body body sort -nr
```

#### Capitalize each value in the body using Ruby

```sh
printf "first_name\njim\nbob\nmary\n" | body ruby -nle 'puts $_.capitalize'
```

#### Use with awk to filter values

```sh
printf "name,score\nAlice,90\nBob,80\nCarol,95\n" | body awk -F, '$2 > 85'
```

## `cols`

This command applies a shell command to a subset of columns in a CSV file and merges the result back with the remaining columns. It is useful for transforming, filtering, or analyzing specific columns while preserving the overall structure. The input must be comma-delimited and have a header. Supports selecting columns to include or exclude, and works with any command that reads from stdin.

**Dependencies:** Bash, csvkit (`csvcut`), paste, tee, mktemp (standard Unix utilities)

### Usage

```sh
cols <column_arg> <columns> <command> [args...]
```

### Arguments

- `<column_arg>`: Column selection argument (`-c` to select specified columns, `-C` to select all except specified columns)
- `<columns>`: Column names or numbers to select or exclude
- `<command> [args...]`: Shell command to apply to the selected columns

### Options

- `-h`, `--help`: Show help message and exit

### Features

- Select columns to process or exclude using `-c` or `-C`
- Applies any shell command to the selected columns
- Merges processed columns back with the remaining columns
- Handles temporary files securely and cleans up after execution
- Validates dependencies and arguments for robust error handling

### Examples

#### Reverse sort column 'a'

```sh
echo 'a,b\n1,2\n3,4\n5,6' | cols -c a body sort -nr
```

#### Apply PCA to all numerical features except 'species' (using tapkee)

```sh
< iris.csv cols -C species body tapkee --method pca | header -r x,y,species
```

#### Select and uppercase a column

```sh
echo 'name,score\nAlice,90\nBob,80' | cols -c name body awk '{print toupper($0)}'
```

#### Exclude a column and process the rest

```sh
echo 'id,value,flag\n1,10,A\n2,20,B' | cols -C flag body awk -F, '{print $1+$2}'
```

## `csv2html`

This command converts CSV data to a complete HTML document with a styled table. It reads CSV from stdin, validates and normalizes the data, and outputs a ready-to-use HTML file. Supports custom delimiters, quote characters, whitespace trimming, skipping empty lines, and strict column validation. Output can be sent to stdout or a file. Robust error handling is included for invalid input and file operations.

**Dependencies:** Python 3, tabulate

### Usage

```sh
cat data.csv | csv2html [options]
```

### Options

- `-d, --delimiter <char>`: Specify the CSV delimiter (default: ',')
- `-q, --quote-char <char>`: Specify the quote character (default: '"')
- `-s, --suppress`: Suppress data rows (output headers only)
- `-o, --output <file>`: Output file path (default: stdout)
- `--skip-empty-lines`: Skip empty lines in CSV parsing (default: True)
- `--no-skip-empty-lines`: Do not skip empty lines
- `--trim-whitespace`: Trim whitespace from all cells (default: True)
- `--no-trim-whitespace`: Do not trim whitespace from cells
- `--strict-columns`: Fail on inconsistent column counts

### Features

- Converts CSV to a complete HTML document with a styled table
- Supports custom delimiters and quote characters
- Optionally suppresses data rows (headers only)
- Trims whitespace and skips empty lines for clean output
- Normalizes inconsistent rows (pads/truncates as needed)
- Strict column validation option for data integrity
- Outputs to stdout or a file
- Robust error handling for invalid input and file operations

### Examples

#### Convert CSV to HTML (default settings)

```sh
cat data.csv | csv2html > output.html
```

#### Use a custom delimiter and output to file

```sh
cat data.tsv | csv2html -d $'\t' -o table.html
```

#### Suppress data rows (headers only)

```sh
cat data.csv | csv2html -s
```

#### Do not trim whitespace or skip empty lines

```sh
cat messy.csv | csv2html --no-trim-whitespace --no-skip-empty-lines
```

#### Strict column validation (fail on inconsistent rows)

```sh
cat inconsistent.csv | csv2html --strict-columns
```

#### Example: Convert CSV and open in browser

```sh
cat data.csv | csv2html -o table.html && xdg-open table.html
```

## `dseq`

This command generates a sequence of dates relative to a start day, with flexible options for formatting, increments, and base date. It is useful for creating time series, scheduling, or any task requiring a list of dates. The script uses the `date` command and supports custom formats and offsets. Robust error handling and input validation are included.

**Dependencies:** Bash, GNU coreutils (`date`, `seq`), mktemp

### Usage

```sh
dseq [OPTIONS] LAST
dseq [OPTIONS] FIRST LAST
dseq [OPTIONS] FIRST INCREMENT LAST
```

### Arguments

- `LAST`: The last offset in days from the base date. If only `LAST` is given, it implies `FIRST=1` and `INCREMENT=1`.
- `FIRST`: The starting offset in days from the base date.
- `INCREMENT`: The step size in days for the sequence.

### Options

- `-f, --format <format_string>`: Specify the output date format (e.g., `%Y-%m-%d`, `%A, %B %d, %Y`). Uses `date` command format codes. Default: `+%F` (YYYY-MM-DD).
- `-s, --start-date <date_string>`: Specify the base date to start from (e.g., `2023-01-01`, `tomorrow`, `yesterday`). Default: today. This affects the `0 day` offset.
- `-h, --help`: Display help message and exit.

### Features

- Generate date sequences with custom increments and ranges
- Flexible date formatting using `date` format codes
- Specify any base date (absolute or relative)
- Validates input and handles edge cases (e.g., zero increment, invalid ranges)
- Secure handling of temporary files

### Examples

#### Generate Tomorrow's Date

```sh
dseq 1
```
Output: Tomorrow's date (default: start=today, first=1, inc=1, last=1)

#### Generate Today's Date

```sh
dseq 0 0
```
Output: Today's date (start=today, first=0, last=0)

#### Generate Next 7 Days

```sh
dseq 7
```
Output: Dates for the next 7 days (start=today, first=1, inc=1, last=7)

#### Generate a Range of Dates

```sh
dseq -2 0
```
Output: Dates from the day before yesterday to today (start=today, first=-2, inc=1, last=0)

#### Generate Weekly Dates for a Year

```sh
dseq 1 7 365
```
Output: Dates starting tomorrow and then every week for a year (start=today, first=1, inc=7, last=365)

#### Custom Date Format

```sh
dseq -f "%Y/%m/%d %a" 0 2
```
Output: Today, tomorrow, and the day after tomorrow in `YYYY/MM/DD Day` format

#### Start from a Specific Date

```sh
dseq -s "2024-12-25" 0 2
```
Output: Dates starting from December 25, 2024

#### Generate Dates Relative to a Specific Day

```sh
dseq -s "last friday" -1 0
```
Output: Dates for last Friday and Saturday

## `header`

This command adds, replaces, deletes, or transforms header lines in tabular or structured text data. It is useful for managing headers in CSV, TSV, or similar formats, and can handle multi-line headers. The script supports applying shell expressions to the header, and works well in CLI data pipelines.

**Dependency:** Bash (no external dependencies)

### Usage

```sh
header [OPTIONS]
```

### Options

- `-n <num>`: Number of lines to consider as header (default: 1)
- `-a <header>`: Add header (prepends header to input)
- `-r <header>`: Replace header (replaces existing header with new header)
- `-e <expr>`: Apply shell expression to header (e.g., `tr "[:upper:]" "[:lower:]"`)
- `-d`: Delete header (removes header lines)
- `-h`: Show help message

### Features

- Add, replace, delete, or transform header lines
- Supports multi-line headers via `-n`
- Apply shell expressions to header for transformation
- Validates arguments and prevents unsafe expressions
- Integrates with other CLI tools for data wrangling

### Examples

#### Add a header to a sequence

```sh
seq 10 | header -a 'values'
```

#### Replace header and transform to lowercase

```sh
seq 10 | header -a 'VALUES' | header -e 'tr "[:upper:]" "[:lower:]"'
```

#### Delete header

```sh
seq 10 | header -a 'values' | header -d
```

#### Add a multi-line header and join with underscore

```sh
seq 10 | header -a 'multi\nline' | header -n 2 -e "paste -sd_"
```

## `scrape`

This command extracts HTML elements from a document using XPath queries or CSS3 selectors. It supports extracting attributes, checking element existence, and outputting results with optional HTML tags. The script is written in Python and uses `lxml` for parsing and `cssselect` for CSS selector support. Input can be read from stdin or a file, and multiple selectors can be processed in one call.

**Dependencies:** Python 3, lxml, cssselect (optional for CSS selectors)

### Usage

```sh
scrape [HTML] [options]
```

### Arguments

- `HTML`: Input HTML file (default: stdin)

### Options

- `-a, --attribute <attr>`: Extract a specific attribute from the HTML tag (e.g., `href`, `src`)
- `-b, --include_body_tags`: Enclose the output with `<html>` and `<body>` tags
- `-e, --selectors <selector>`: Specify XPath queries or CSS3 selectors to extract elements (can be used multiple times)
- `-f, --input_file <file>`: Specify a file to read the HTML input from instead of `stdin`
- `-x, --check_existence`: Exit with code `0` if elements exist, otherwise exit with code `1`
- `-r, --raw_input`: Do not parse the HTML before feeding it to `etree` (useful for escaping CData)

### Features

- Extract elements using XPath or CSS selectors (CSS selectors require `cssselect`)
- Extract specific attributes from tags
- Output results with optional HTML and BODY tags
- Check for existence of elements and exit with appropriate code
- Read input from stdin or file
- Process multiple selectors in one call
- Robust error handling and input validation

### Examples

#### Extract Links from a Webpage

```sh
curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s | scrape -e 'a' -a 'href'
```

#### Extract Table Data Using CSS Selectors

```sh
curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s | scrape -e 'table.wikitable > tbody > tr > td > b > a'
```

#### Extract Specific Attributes

```sh
curl 'https://example.com' -s | scrape -e 'img' -a 'src'
```

#### Check Existence of Elements

```sh
curl 'https://example.com' -s | scrape -e 'div#main-content' -x
```

#### Process Raw HTML Input

```sh
cat raw_html_file.html | scrape -r -e '//div[@class="content"]'
```

#### Include HTML and BODY Tags in Output

```sh
curl 'https://example.com' -s | scrape -e 'p' -b
```

#### Read HTML from a File

```sh
scrape -f input.html -e 'h1'
```

#### Extract Multiple Selectors

```sh
scrape -e 'h1' -e 'h2' -e 'h3' -f page.html
```

> [!Tip]
> - CSS Selectors: If a selector is provided, it is automatically converted to XPath using `cssselect`.
> - XPath Queries: XPath expressions can be used directly by prefixing them with `//`.

## `httpservedir`

This command serves static files from a specified directory over HTTP using Python's built-in HTTP server. It validates the port and directory before starting, and provides clear error messages for invalid input. Useful for quickly sharing files or hosting simple static sites from the CLI.

**Dependencies:** Bash, Python 3

### Usage

```sh
httpservedir [PORT] [DIR]
```

### Arguments

- `PORT`: Port number to serve on (default: `8000`). Must be between 1 and 65535.
- `DIR`: Directory to serve (default: current working directory).

### Features

- Serves static files from any directory using Python's HTTP server
- Validates port number and directory existence
- Provides clear error messages for invalid input
- Defaults to port 8000 and current directory if not specified
- Integrates easily into CLI workflows

### Examples

#### Serve Current Directory on Default Port

```sh
httpservedir
```

## `plot`

This command generates various types of terminal plots (line, scatter, bar, time series) from JSON data using Python. It supports both ASCII and gnuplot-based visualizations, making it suitable for quick data exploration in the CLI. The script automatically detects the plot type and keys, and can read data from stdin or a file.

**Dependencies:** Python 3, termplotlib, gnuplot (for some plot types)

### Usage

```sh
plot --type <plot_type> [--data <file>] [--xkey <key>] [--ykey <key>] [--title <title>]
```

### Arguments

- `-t`, `--type <plot_type>`: Type of plot to generate. Choices: `line`, `scatter`, `vertical_bar`, `horizontal_bar`, `time_series` (required)
- `-d`, `--data <file>`: Input data in JSON format (default: stdin)
- `-x`, `--xkey <key>`: Key for X-axis values in JSON data (default: `x`)
- `-y`, `--ykey <key>`: Key for Y-axis values in JSON data (default: `y`)
- `-T`, `--title <title>`: Title of the chart (optional)

### Features

- Supports line, scatter, vertical bar, horizontal bar, and time series plots
- Reads data from stdin or a file in JSON format
- Uses termplotlib for ASCII plots and gnuplot for advanced terminal plots
- Customizable axis keys and chart title
- Validates input and provides error messages for invalid data

### Examples

#### Line Plot from JSON

```sh
echo '[{"hours": 0, "sales": 0}, {"hours": 1, "sales": 2}]' | plot --type line --xkey "hours" --ykey "sales" --title "Sales Over Time"
```

#### Scatter Plot

```sh
echo '[{"x": 1, "y": 2}, {"x": 2, "y": 3}]' | plot --type scatter
```

#### Vertical Bar Chart

```sh
echo '[{"category": "A", "value": 10}, {"category": "B", "value": 20}]' | plot --type vertical_bar --xkey "category" --ykey "value"
```

#### Horizontal Bar Chart

```sh
echo '[{"label": "X", "score": 5}, {"label": "Y", "score": 8}]' | plot --type horizontal_bar --xkey "label" --ykey "score"
```

#### Time Series Plot

```sh
echo '[{"date": "2025-07-01", "value": 10}, {"date": "2025-07-02", "value": 20}]' | plot --type time_series --xkey "date" --ykey "value" --title "Values Over Time"
```

## `trim`

This command trims the output to a specified height (number of lines) and width (number of characters per line). It is useful for limiting the size of terminal output, especially when working with large datasets or long lines of text. Tabs are expanded to spaces before trimming. If the output exceeds the specified height, a summary of the remaining lines is shown. If terminal width cannot be determined, it defaults to 80 characters.

**Dependency:** Bash, awk, expand, tput

### Usage

```sh
trim [height] [width]
trim --help
```

### Arguments

- `height`: Maximum number of lines to display (default: 10). Use -1 to disable height limiting.
- `width`: Maximum character width per line (default: terminal width). Use -1 to disable width limiting.

### Features

- Height trimming: limits the number of lines displayed, shows summary if output exceeds height
- Width trimming: limits the number of characters per line, truncates and appends `…` if exceeded
- Tabs expansion: tabs are converted to spaces before trimming
- Fallback width: defaults to 80 characters if terminal width cannot be determined
- Robust argument validation and error handling

### Examples

#### Trim Output to Default Height and Width

```sh
seq 100 | trim
```

#### Trim Output to a Specific Height

```sh
seq 100 | trim 20
```

#### Trim Output to a Specific Height and Width

```sh
seq 100 | trim 20 40
```

#### Disable Height Trimming

```sh
seq 100 | trim -1 40
```

#### Disable Width Trimming

```sh
seq 100 | trim 20 -1
```

## `unpack`

This command extracts common archive file formats to a target directory. It supports a wide range of formats and automatically selects the appropriate extraction tool. Useful for batch extraction and automation in CLI workflows. The script validates files, checks dependencies, and provides verbose and dry-run modes for safe operation.

**Dependencies:** Bash, unrar, unzip, p7zip-full, tar, gzip, bzip2, ar, bunzip2, gunzip, uncompress

### Usage

```sh
unpack [-h] [-d TARGET_DIR] [-c NEW_DIR] [-v] [-n] <archive> [archive2 ...]
```

### Arguments

- `<archive>`: One or more archive files to extract

### Options

- `-h`: Show help message
- `-d TARGET_DIR`: Target directory for extraction (default: current directory)
- `-c NEW_DIR`: Create new directory and extract content inside it
- `-v`: Verbose output (shows info messages)
- `-n`: Dry run (shows what would be done without executing)

### Features

- Supports batch extraction of multiple files
- Automatically detects and extracts supported formats
- Creates new directories for extraction when needed
- Validates files and target directory before extraction
- Checks for required dependencies and warns if missing
- Verbose and dry-run modes for safe operation
- Robust error handling and logging

### Supported Formats

- .7z, .tar.bz2, .bz2, .deb, .tar.gz, .gz, .tar, .tbz2, .tar.xz, .tgz, .rar, .zip, .Z

### Examples

#### Extract a zip file to the current directory

```sh
unpack archive.zip
```

#### Extract multiple archives to a specific directory

```sh
unpack -d /tmp/extracted archive1.tar.gz archive2.zip
```

#### Create a new directory and extract content inside it

```sh
unpack -c extracted_files archive.tar.gz
```

#### Show what would be done (dry run)

```sh
unpack -n archive.tar.bz2
```

#### Verbose extraction

```sh
unpack -v archive.rar
```

#### Create directory with verbose output

```sh
unpack -c my_archive -v archive.zip
```
