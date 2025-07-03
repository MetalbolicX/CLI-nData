# Getting Started with CLI-nData

## Prerequisites

Ensure you have Python 3.8 or higher installed on your system. You can check your Python version by running:

```sh
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

!> Make sure to have `pip` installed, which is the package installer for Python.

## Installation

1. Clone the CLI-nData repository from GitHub:

```sh
git clone https://github.com/MetalbolicX/cli-ndata
```

2. Add the CLI-nData directory to your PATH by executing the following command in your terminal:

```sh
export PATH="$HOME/cli-ndata:$PATH"
```

This command will allow you to run CLI-nData commands from anywhere in your terminal, similar to how you use commands like `cd` or `cat`. You can add this line to your `.bashrc` or `.zshrc` file to make it permanent.

3. To verify the installation, run:

```sh
curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be 'table.wikitable > tbody > tr  > td > b > a'
```

This command should output a HTML with the list of sovereign states, indicating that CLI-nData is working correctly.
