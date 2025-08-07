# Count Tokens

This Python module uses the tiktoken library to count the number of tokens in a text file or a string.

## Use Case

Use this module when you want to quickly determine the number of tokens in a file or a string but don't want to post your data to a public site like <https://platform.openai.com/tokenizer>.

## Usage

To use this module, pass the file path of the file for which you want to count tokens as a command line argument. For example:

`python count_tokens.py your_file.txt`

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

After install you can either:

```shell
poetry run count-tokens your_file.txt
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
