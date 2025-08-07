# pylint: disable=redefined-outer-name
"""Unit tests for the count_tokens module."""
import os
import sys
import tempfile
import textwrap

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

    per_file, total = count_tokens.analyze_directory(str(tmp_path))
    # Basic sanity: both files counted, total equals sum.
    assert len(per_file) == 2
    assert total == sum(per_file.values())


def test_directory_analysis_ignores_node_modules(tmp_path):
    """Files in node_modules should be ignored."""
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.js").write_text(
        "console.log('ignore me')", encoding="utf-8"
    )
    kept = tmp_path / "keep.py"
    kept.write_text("print('hi')", encoding="utf-8")

    per_file, total = count_tokens.analyze_directory(str(tmp_path))
    assert str(kept) in per_file
    assert not any("pkg.js" in p for p in per_file)
    assert total == per_file[str(kept)]


def test_directory_analysis_keeps_non_ignored_files(tmp_path):
    """Non-ignored files should be present in results."""
    kept = tmp_path / "keep.py"
    kept.write_text("print('hi')", encoding="utf-8")

    per_file, total = count_tokens.analyze_directory(str(tmp_path))
    assert list(per_file.keys()) == [str(kept)]
    assert total == per_file[str(kept)]


def test_directory_custom_ignore_file(tmp_path):
    """A custom .tokenizerignore should augment (and de-duplicate) defaults."""
    (tmp_path / "data").mkdir()
    inc = tmp_path / "data" / "include.txt"
    exc_dir = tmp_path / "skipme"
    exc_dir.mkdir()
    inc.write_text("some content here", encoding="utf-8")
    (exc_dir / "ignored.txt").write_text("should not count", encoding="utf-8")
    # Custom ignore file
    (tmp_path / ".tokenizerignore").write_text(
        textwrap.dedent(
            """
            # Comment line
            skipme/
            """
        ).strip(),
        encoding="utf-8",
    )

    per_file, total = count_tokens.analyze_directory(str(tmp_path))
    assert str(inc) in per_file
    # Ensure directory skip worked.
    assert not any("ignored.txt" in p for p in per_file)
    # Total should at least include the included file; ensure ignore file
    # skipped.
    assert per_file[str(inc)] <= total
    assert not any(p.endswith(".tokenizerignore") for p in per_file)


def test_directory_analysis_ignores_binary_files(tmp_path):
    """Binary files should be ignored."""
    binary_file = tmp_path / "file.pyc"
    binary_file.write_bytes(b"\x00\x01\x02\x03\x04")
    kept = tmp_path / "keep.py"
    kept.write_text("print('hi')", encoding="utf-8")

    per_file, total = count_tokens.analyze_directory(str(tmp_path))
    assert str(kept) in per_file
    assert str(binary_file) not in per_file
    assert total == per_file[str(kept)]
