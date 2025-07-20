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

This command converts CSV data to a complete HTML document.

**Dependencies:** Deno standard library (Deno must be installed)

### Usage

```sh
cat data.csv | csv2html [options]
```

### Options

- `-d, --delimiter <char>`: Specify the CSV delimiter (default: ',').
- `-f`, `--fields <number>`: Specify the number of fields to include in the HTML table (default: all fields as 0).
- `-H`, `--header`: Indicates the first line does not contain headers.
- `-h, --help`: Show help message and exit.
- `-o, --output <file>`: Output HTML to a file instead of stdout

### Examples

#### Convert CSV to HTML and prints on stdout (default settings)

```sh
cat data.csv | csv2html
```

#### Use a custom delimiter and output to file

```sh
cat data.tsv | csv2html -d '\t' -o table.html
```

#### Indicates the first line does not contain headers

```sh
cat data.csv | csv2html -H
```

#### Indicates the number of fields to include in the HTML table

```sh
cat inconsistent.csv | csv2html -f 3
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

- `-n <number>`: Number of lines to consider as header (default: 1).
- `-a <header>`: Add header (prepends header to input).
- `-r <header>`: Replace header (replaces existing header with new header).
- `-e <expr>`: Apply shell expression to header (e.g., `tr "[:upper:]" "[:lower:]"`).
- `-d`: Delete header (removes header lines).
- `-h`: Show help message.

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

This command extracts information from a HTML document. It supports XPath or CSS selectors to specify which elements to extract, and can output specific attributes from those elements.

**Dependencies:** Deno standard library, node-html-parser, xPathToCss packages.

### Usage

```sh
scrape [HTML] [options]
```

### Arguments

- `HTML`: Input HTML file (default: stdin)

### Options

- `-a, --attribute <attr>`: Extract a specific attribute from the HTML tag (e.g., `href`, `src`).
- `-d`, `--data <schema>`: Use a specific schema to extract the attributes or information of an element.
- `-e`, `--extracts <selectors>`: Extract information of multiple selectors.
- `-h`, `--help`: Show help message.
- `-o`, `--output <file>`: Output to a file instead of stdout.
- `-s`, `--selector <selector>`: A CSS selector or XPath to extract elements.
- `-t`, `--text`: Extract text content from the selected elements.
- `-x`, `--exists`: Check if the selected elements exist in the HTML document.

### Examples

#### Extract Links from a Webpage

```sh
curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s | scrape -s 'a' -a 'href'
```

#### Extract the HTML of all Links inside a Table

```sh
curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s | scrape -s 'table.wikitable > tbody > tr > td > b > a'
```

#### Extract Specific Attributes

```sh
curl 'https://books.toscrape.com/' -s | scrape -s 'img' -a 'src'
```

#### Check Existence of Elements

```sh
curl 'https://books.toscrape.com/' -s | scrape -s 'header' -x
```

#### Extract Text Content

```sh
curl 'https://books.toscrape.com/' -s | scrape -s 'h3 a' -t
```

#### Schema Extraction

```sh
curl -s "https://books.toscrape.com/" | scrape -s '.side_categories li a' -d '{
    "content": "textContent",
    "url": "href"
}'
```

> [!Note]
> The `-d` option allows you to define a schema (object in JSON format) to extract specific attributes or information from the selected elements. The result will have a JSON structure based on the schema provided.

#### Extract Multiple Selectors

```sh
curl -s "https://books.toscrape.com/" | scrape -e '[
	{"selector":"article.product_pod p.price_color",
	"schema":{
		"content":"textContent"
		}
	},
	{"selector":"article.product_pod a",
	"schema":{
		"content":"textContent",
		"url": "href"
		}
	}
]'
```

> [!Note]
> The `-e` option allows you to extract information from multiple selectors at once. Each selector can have its own schema for extracting attributes or text content. It's necessary to use the `schema` key to define how to extract the information from each selector.

## `httpservepwd`

This command starts a static HTTP server in the current working directory, serving files over HTTP. It is useful for quickly sharing files or directories without needing a full web server setup. It also has the ability to restart the server when a file changes.

**Dependencies:** Python 3 reloadserver package.

### Usage

```sh
httpservepwd
```

## `plot`

This command generates various types of terminal plots (line, scatter, bar, time series) from JSON data. It uses ASCII based visualizations, making it suitable for quick data exploration in the CLI..

**Dependencies:** Deno and chartex package.

### Usage

```sh
plot [DATA] [OPTIONS]
```

### Arguments

- `DATA`: Input data in JSON format (default: stdin). The data should be an array of objects with consistent keys.

### Options

- `-t`, `--type <type>`: Type of plot to generate (default: `line`). Options: `line`, `scatter`, `vertical_bar`, `horizontal_bar`, `time_series`.
- `-x`, `--xkey <key>`: Key for x-axis values (required for most plots).
- `-y`, `--ykey <key>`: Key for y-axis values (required for most plots).
- `-T`, `--title <title>`: Title of the chart (default: `Plot`).
- `-h`, `--help`: Show help message and exit.

### Examples

#### Line Plot from JSON

```sh
echo '[{"hours": 0, "sales": 0}, {"hours": 1, "sales": 2}]' | plot -t line -x "hours" -y "sales"
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
