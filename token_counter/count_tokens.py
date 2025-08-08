"""Count tokens for a file or an entire directory tree.

This module uses the *tiktoken* library to count the number of tokens in
either (a) a single file or (b) every file within a directory tree.

Directory mode supports an ignore file (``.tokenizerignore``) whose
semantics are intentionally similar to a very small subset of
``.gitignore``: each non-empty, non-comment line is treated as a shell
style glob pattern (``fnmatch``) against the root-relative path of a file
or directory. A trailing ``/`` on a pattern is ignored and is equivalent
to the directory name alone. If an ignore file is not present, no files
are ignored (all files in the directory tree are processed).

Functions:
    read_file: Return the content of a file as a string.
    process_tokens: Return the number of tokens in a string.
    load_ignore_patterns: Load ignore patterns from file.
    iter_files: Yield file paths under a directory honoring ignore rules.
    analyze_directory: Return processed files and total token counts.
    main: CLI entrypoint.

Usage examples:
    python count_tokens.py some_file.py
    python count_tokens.py path/to/project_dir
"""

import argparse
import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Set, Tuple

import tiktoken

# Name of the ignore file to look for in directory analysis
IGNORE_FILE_NAME = ".tokenizerignore"


def parse_arguments():
    """Parse command line arguments.

    The single positional argument can be either a file OR a directory.
    """
    parser = argparse.ArgumentParser(
        description=("Count tokens in a file OR recursively in a directory tree.")
    )
    parser.add_argument(
        "input_fp",
        type=str,
        help="Path to a file or directory to analyze",
    )
    return parser.parse_args()


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
          Ref:
            https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
            https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

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


def load_ignore_patterns(
    root: str, ignore_filename: str = IGNORE_FILE_NAME
) -> List[str]:
    """Load ignore patterns from an ignore file.

    Args:
        root: Directory root being analyzed.
        ignore_filename: Name of the ignore file to look for.

    Returns:
        List of glob patterns from the ignore file, or empty list if file not found.
    """
    candidate = os.path.join(root, ignore_filename)
    patterns: List[str] = []
    try:
        with open(candidate, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.endswith("/"):
                    line = line[:-1]
                patterns.append(line)
    except FileNotFoundError:
        patterns = []
    return patterns


def _is_ignored(rel_path: str, patterns: List[str]) -> bool:
    """Return True if rel_path matches any ignore pattern.

    Matching strategy: pattern is applied both to the full root-relative
    path and to each individual path component, using fnmatch.
    """
    normalized_path = Path(rel_path).as_posix()
    path_segments = normalized_path.split("/")

    # Convert patterns to set for faster lookups when doing exact matches
    pattern_set = set(patterns)

    # First check for exact matches (fast path)
    if normalized_path in pattern_set:
        return True
    if any(segment in pattern_set for segment in path_segments):
        return True

    # Then check for glob pattern matches
    for pattern in patterns:
        if fnmatch(normalized_path, pattern):
            return True
        if any(fnmatch(segment, pattern) for segment in path_segments):
            return True
    return False


def traverse_files(root: str, patterns_to_ignore: List[str]) -> Iterable[str]:
    """Yield file paths under root honoring ignore patterns.

    Args:
        root: Directory root to traverse
        patterns_to_ignore: List of glob patterns to ignore
    """

    for dir_path, dir_names, file_names in os.walk(root):
        relative_directory = os.path.relpath(dir_path, root)
        if relative_directory == ".":
            relative_directory = ""
        # Modify dirnames in place to prune traversal early.
        pruned_directory_names = []
        for dir_name in list(dir_names):
            relative_subdirectory = (
                os.path.join(relative_directory, dir_name)
                if relative_directory
                else dir_name
            )
            if _is_ignored(relative_subdirectory, patterns_to_ignore):
                pruned_directory_names.append(dir_name)
        for dir_name in pruned_directory_names:
            dir_names.remove(dir_name)

        for file_name in file_names:
            rel_file = (
                os.path.join(relative_directory, file_name)
                if relative_directory
                else file_name
            )
            if _is_ignored(rel_file, patterns_to_ignore):
                continue
            yield os.path.join(dir_path, file_name)


def _is_binary_file(fp: str, chunk_size: int = 1024) -> bool:
    """Return True if the file appears to be binary."""
    try:
        with open(fp, "rb") as f:
            chunk = f.read(chunk_size)
            # If there are null bytes or non-text bytes, treat as binary.
            if b"\x00" in chunk:
                return True
            # Try decoding as UTF-8; if it fails, it's likely binary.
            try:
                chunk.decode("utf-8")
            except UnicodeDecodeError:
                return True
    except Exception:
        # If we can't open/read, treat as binary to be safe.
        return True
    return False


def analyze_directory(directory: str) -> Tuple[Set[str], int]:
    """Analyze every file within a directory tree.

    Args:
        directory: Path to directory to analyze.

    Returns:
        (set of processed file paths, total token count)

    Raises:
        ValueError: If no tokens are found across all files.
    """
    ignored_patterns = load_ignore_patterns(directory)
    processed_files: Set[str] = set()
    total_tokens = 0
    for fp in traverse_files(directory, ignored_patterns):
        if _is_binary_file(fp):
            continue
        try:
            content = read_file(fp)
        except (FileNotFoundError, UnicodeDecodeError):
            # Skip transient and unreadable files.
            continue
        try:
            count = process_tokens(content)
        except ValueError:
            # Skip empty files.
            continue
        processed_files.add(fp)
        total_tokens += count

    if total_tokens == 0:
        raise ValueError("No tokens found in directory (all files empty or ignored).")
    return processed_files, total_tokens


def main():
    """
    Orchestrator function.

    Parses command line arguments, processes tokens in the input file,
    and prints the token count. Exits with status code 1 if an
    error occurs, or 0 otherwise.
    """
    try:
        args = parse_arguments()
        input_path = args.input_fp
        if os.path.isdir(input_path):
            processed_files, total_tokens = analyze_directory(input_path)
            print(
                "Total tokens in directory '"
                f"{input_path}': {total_tokens} across "
                f"{len(processed_files)} files."
            )
        else:
            input_str = read_file(input_path)
            token_count = process_tokens(input_str)
            print(f"The number of tokens in the input file is: {token_count}.")
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc))
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
