"""Count the number of tokens in a text string using tiktoken.

This module counts the number of tokens in a text string using the 
tiktoken library.

Functions:
        read_file: Returns the content of a file as a string.
        process_tokens: Returns the number of tokens from a string.
        main: The module orchestrator.
        

Usage example:
    python count_tokens.py your_file.cs
"""

import argparse
import sys
import tiktoken


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Count the number of tokens in a text file."
    )
    parser.add_argument("input_fp", type=str, help="The input file path")
    args = parser.parse_args()
    return args


def read_file(input_fp):
    """Return the contents of a text file.

    Args:
        input_fp (str): The path for the input file.

    Raises:
        FileNotFoundError: If the input file is not found.

    Returns:
        str: The file content.
    """
    try:
        with open(input_fp, "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError as e:
        print(f"File not found: {str(e)}")
        raise


def process_tokens(input_str, token_reference_model="gpt-4"):
    """Return the token count from an input string.

    Args:
        input_str (str): The input string.
        token_reference_model (str, optional): Choose an encoding
          based on a reference model. Defaults to "gpt-4" which uses
          cl100k_base.
          Ref: https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken

    Raises:
        ValueError: If no tokens are found in the input string.

    Returns:
        int: The number of tokens in the input string.
    """
    encoding = tiktoken.encoding_for_model(token_reference_model)

    token_count = len(encoding.encode(input_str))

    if not token_count:
        raise ValueError("No tokens found in the input string.")

    return token_count


def main():
    """
    Orchestrator function.

    Parses command line arguments, processes tokens in the input file,
    and prints the token count. Exits with status code 1 if an
    error occurs, or 0 otherwise.
    """
    try:
        args = parse_arguments()
        input_fp = args.input_fp
        input_str = read_file(input_fp)
        token_count = process_tokens(input_str)
    except ValueError:
        sys.exit(1)
    except FileNotFoundError:
        sys.exit(1)

    print(f"The number of tokens in the input file is: {token_count}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
