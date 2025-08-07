# Count Tokens

This Python module uses the tiktoken library to count the number of tokens in a text file or a string.

## Use Case

Use this module when you want to quickly determine the number of tokens in a file or a string but don't want to post your data to a public site like <https://platform.openai.com/tokenizer>.

## Usage

### Single File

Pass the file path of the file for which you want to count tokens as a
command line argument. For example:

```shell
python token_counter/count_tokens.py your_file.txt
```

Or after installing via poetry:

```shell
poetry run count-tokens your_file.txt
```

### Directory (Recursive) Mode

Provide a directory path instead of a file and the tool will walk the
entire tree, summing the tokens for every readable text file that is
not excluded by the ignore rules.

```shell
poetry run count-tokens path/to/project_dir
```

Output example:

```text
Total tokens in directory 'path/to/project_dir': 12345 across 87 files.
```

Binary files (or files that cannot be decoded as UTF‑8) are skipped
silently. Empty files contribute zero tokens and are omitted from the
file count.

### Ignore File (.tokenizerignore)

Directory mode looks for a file named `.tokenizerignore` at the root of
the directory you pass. Each non‑blank, non‑comment line is treated as a
glob pattern (similar to a very small subset of `.gitignore` syntax) and
matched against both full relative paths and individual path segments.

An example (the default file shipped with this repository):

```text
# Python
__pycache__/
*.pyc
.venv/

# Node
node_modules/

# Git / Tooling
.git/
.vscode/
```

If no `.tokenizerignore` exists, a built‑in default set of patterns for
common Python / Node / Git clutter is used automatically so you still
avoid counting dependencies and build artifacts.

You can customize exclusions by editing or creating `.tokenizerignore`.
Patterns are simple shell globs (handled with Python `fnmatch`). A
trailing `/` is optional and only used for readability.

## Dependencies & Tooling

This project uses:

- Python ^3.12
- [Poetry](https://python-poetry.org/) (dependency management)
- `tiktoken` (runtime dependency)
- `pytest` (dev dependency)

## Installation

To use this module, follow these steps:

### Clone the repository

Clone the repository to your local machine and navigate to the project directory

```shell
# SSH
git clone git@github.com:binarysubstrate/token-counter.git

# HTTPS
git clone https://github.com/binarysubstrate/token-counter.git


```

### Set Python version (pyenv)

Install Python ^3.12 if you don't have it yet:

```shell
# Example
# Skip if installed
pyenv install 3.31.1  
```

Set the local version (writes `.python-version`):

```shell
pyenv local 3.31.1  
```

On Windows (pyenv-win) the commands are the same once pyenv-win is installed.

### Install Poetry

If Poetry is not installed:

```shell
pip install --user poetry  # or follow official installer instructions
```

### Install dependencies

From the project root:

```shell
poetry install
```

### Using the CLI script

After install you can either run against a single file or a directory:

```shell
poetry run count-tokens path/to/file.py
poetry run count-tokens path/to/dir
```

## Running Tests

If you'd like to run the tests for this module, use the pytest command:

```shell
poetry run pytest
```

The test configuration is in `pyproject.toml` (quiet mode by default).

## Links

- OpenAI tiktoken library ([GitHub](https://github.com/openai/tiktoken))
- How to count tokens with Tiktoken ([OpenAI](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken))
