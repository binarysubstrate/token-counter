# pylint: disable=redefined-outer-name
"""Unit tests for the count_tokens module."""
import os
import sys
import tempfile

import pytest

from token_counter import count_tokens

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
    """Failing to include a file to parse should cause a system exit."""
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
    """A non-existent file should cause a system exit from main."""
    sys.argv = ["count_tokens.py", "non_existent_file.txt"]
    with pytest.raises(SystemExit) as cm:
        count_tokens.main()
    assert cm.value.code == EXIT_GENERAL_FAILURE


def test_full_run_success(test_file):
    """A valid run from main should return a success code."""
    sys.argv = ["count_tokens.py", test_file]
    with pytest.raises(SystemExit) as cm:
        count_tokens.main()
    assert cm.value.code == EXIT_SUCCESS


def test_directory_analysis_basic(tmp_path):
    """Analyzing a directory should sum token counts across files."""
    file1 = tmp_path / "a.txt"
    file1.write_text("hello world", encoding="utf-8")
    file2 = tmp_path / "b.txt"
    file2.write_text("another file", encoding="utf-8")

    processed_files, total = count_tokens.analyze_directory(str(tmp_path))
    # Basic sanity: both files counted
    assert len(processed_files) == 2
    assert str(file1) in processed_files
    assert str(file2) in processed_files


def test_directory_analysis_ignores_node_modules(tmp_path):
    """Files in node_modules should be ignored when specified in .tokenizerignore."""
    # Create .tokenizerignore file
    (tmp_path / ".tokenizerignore").write_text("node_modules/", encoding="utf-8")

    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.js").write_text(
        "console.log('ignore me')", encoding="utf-8"
    )
    file_to_keep = tmp_path / "keep.py"
    file_to_keep.write_text("print('hi')", encoding="utf-8")

    processed_files, total_tokens = count_tokens.analyze_directory(str(tmp_path))
    assert total_tokens == 7
    assert len(processed_files) == 2  # keep.py and .tokenizerignore
    assert str(file_to_keep) in processed_files
    assert str(tmp_path / ".tokenizerignore") in processed_files


def test_directory_analysis_keeps_non_ignored_files(tmp_path):
    """Non-ignored files should be present in results."""
    kept = tmp_path / "keep.py"
    kept.write_text("print('hi')", encoding="utf-8")

    processed_files, total = count_tokens.analyze_directory(str(tmp_path))
    assert str(kept) in processed_files
    assert len(processed_files) == 1


def test_directory_custom_ignore_file(tmp_path):
    """Custom ignore patterns should be respected during directory analysis."""
    # Create a custom .tokenizerignore file with specific patterns
    ignore_file = tmp_path / ".tokenizerignore"
    ignore_file.write_text(
        "*.log\ntemp/\n.tokenizerignore\n# Comment line\n\n", encoding="utf-8"
    )

    # Create files that should be ignored
    log_file = tmp_path / "debug.log"
    log_file.write_text("log entry", encoding="utf-8")

    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()
    temp_file = temp_directory / "cache.txt"
    temp_file.write_text("temporary data", encoding="utf-8")

    # Create file that should NOT be ignored
    kept_file = tmp_path / "keep.py"
    kept_file.write_text("print('hello')", encoding="utf-8")

    processed_files, total = count_tokens.analyze_directory(str(tmp_path))

    # Only the kept file should be in results
    assert len(processed_files) == 1
    assert str(kept_file) in processed_files
    assert str(log_file) not in processed_files
    assert str(temp_file) not in processed_files


def test_directory_analysis_ignores_binary_files(tmp_path):
    """Binary files should be ignored."""
    binary_file = tmp_path / "file.pyc"
    binary_file.write_bytes(b"\x00\x01\x02\x03\x04")
    kept = tmp_path / "keep.py"
    kept.write_text("print('hi')", encoding="utf-8")

    processed_files, total = count_tokens.analyze_directory(str(tmp_path))
    assert str(kept) in processed_files
    assert str(binary_file) not in processed_files
    assert len(processed_files) == 1
