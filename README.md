# Count Tokens

This Python module uses the tiktoken library to count the number of tokens in a text file or a string.

## Use Case

Use this module when you want to quickly determine the number of tokens in a file or a string but don't want to post your data to a public site like <https://platform.openai.com/tokenizer>.

## Usage

To use this module, pass the file path of the file for which you want to count tokens as a command line argument. For example:

`python count_tokens.py your_file.txt`

## Dependencies

count-tokens requires:

- Python (>= 3.8)
- tiktoken (>= 0.6)
- pytest (>= 8)

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

### Create virtual environment

Create a virtual environment using venv:

```shell
python -m venv token_counter_venv
```

Activate the virtual environment and install dependencies:

```shell
# On Windows
.\token_counter_venv\Scripts\activate

# On Unix or MacOS
source token_counter_venv/bin/activate

cd token-counter/token_counter

pip install -r ../requirements.txt
```

## Running Tests

If you'd like to run the tests for this module, use the pytest command:

`pytest test_count_tokens.py`

## Links

- OpenAI tiktoken library ([GitHub](https://github.com/openai/tiktoken))
- How to count tokens with Tiktoken ([OpenAI](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken))
