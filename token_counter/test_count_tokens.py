# pylint: disable=redefined-outer-name
"""Unit tests for the count_tokens module."""
import os
import sys
import tempfile

import pytest

import count_tokens

EXIT_SUCCESS = 0
EXIT_GENERAL_FAILURE = 1
EXIT_FAILURE_MISUSE_OF_SHELL_COMMAND = 2


@pytest.fixture
def test_file():
    """Create a temporary file that will be tokenized."""
    temporary_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    temporary_file.write(
        "Imagine this is a large file with a lot of code "
        "and you want an idea of how many tokens it will cost "
        "you to include in your context."
    )
    temporary_file.close()
    yield temporary_file.name
    os.unlink(temporary_file.name)


@pytest.fixture
def empty_file():
    """Create an empty temporary file that will be tokenized."""
    temporary_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    temporary_file.write("")
    temporary_file.close()
    yield temporary_file.name
    os.unlink(temporary_file.name)


def test_parse_arguments_success(test_file):
    """Passing arguments should be successful."""
    sys.argv = ["count_tokens.py", test_file]
    args = count_tokens.parse_arguments()
    assert args.input_fp == test_file


def test_parse_arguments_failure():
    """Failing to include an file to parse should cause a system exit."""
    sys.argv = ["count_tokens.py"]
    with pytest.raises(SystemExit) as cm:
        _ = count_tokens.parse_arguments()
    assert cm.value.code == EXIT_FAILURE_MISUSE_OF_SHELL_COMMAND


def test_process_tokens_success(test_file):
    """The expected token count should be returned."""
    input_str = count_tokens.read_file(test_file)
    token_count = count_tokens.process_tokens(input_str, "gpt-4")
    assert token_count == 30


def test_empty_string_raises_exception():
    """An empty file should raise an exception."""
    with pytest.raises(ValueError) as cm:
        count_tokens.process_tokens("")
    assert str(cm.value) == "No tokens found in the input string."


def test_system_exit_upon_empty_file(empty_file):
    """An empty file causes a system exit from main."""
    sys.argv = ["count_tokens.py", empty_file]
    with pytest.raises(SystemExit) as cm:
        count_tokens.main()
    assert cm.value.code == EXIT_GENERAL_FAILURE


def test_system_exit_upon_non_existent_file():
    """A non-existent file should causes a system exit from main."""
    sys.argv = ["count_tokens.py", "non_existent_file.txt"]
    with pytest.raises(SystemExit) as cm:
        count_tokens.main()
    assert cm.value.code == 1


def test_full_run_success(test_file):
    """A valid run from main should return a success code."""
    sys.argv = ["count_tokens.py", test_file]
    with pytest.raises(SystemExit) as cm:
        count_tokens.main()
    assert cm.value.code == EXIT_SUCCESS
