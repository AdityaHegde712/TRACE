"""
Token verification and comparison CLI utility for measuring structural prompt compression.
Supports measuring individual files or comparing before/after diffs with line, byte, and token metrics.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


def estimate_tokens(text: str) -> int:
    """
    Returns estimated or exact BPE token count.
    Uses tiktoken if installed, otherwise falls back to calibrated heuristic.
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text, disallowed_special=()))
    except ImportError:
        # Standard calibration for mixed Markdown/code (~3.6-3.8 chars/token)
        # Accounts for words, whitespace sequences, punctuation, and markdown delimiters.
        tokens = 0
        words = text.split()
        for word in words:
            tokens += max(1, math.ceil(len(word) / 4))
        # Account for linebreaks and indentation tokens in BPE
        line_count = text.count("\n")
        return max(1, tokens + math.ceil(line_count * 0.75))


def get_file_metrics(file_path: Path) -> dict[str, int]:
    content = file_path.read_text(encoding="utf-8")
    return {
        "lines": len(content.splitlines()),
        "bytes": len(content.encode("utf-8")),
        "chars": len(content),
        "tokens": estimate_tokens(content),
    }


def cmd_measure(file_path_str: str) -> None:
    path = Path(file_path_str)
    if not path.is_file():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    metrics = get_file_metrics(path)
    print(f"Metrics for: {path.name}")
    print(f"  Lines:      {metrics['lines']:,}")
    print(f"  Bytes:      {metrics['bytes']:,}")
    print(f"  Characters: {metrics['chars']:,}")
    print(f"  Tokens:     {metrics['tokens']:,} (estimated BPE)")


def cmd_diff(before_str: str, after_str: str) -> None:
    before_path = Path(before_str)
    after_path = Path(after_str)
    if not before_path.is_file():
        print(f"Error: 'before' file not found: {before_path}", file=sys.stderr)
        sys.exit(1)
    if not after_path.is_file():
        print(f"Error: 'after' file not found: {after_path}", file=sys.stderr)
        sys.exit(1)

    m_before = get_file_metrics(before_path)
    m_after = get_file_metrics(after_path)

    line_diff = m_before["lines"] - m_after["lines"]
    line_pct = (line_diff / m_before["lines"] * 100) if m_before["lines"] else 0

    byte_diff = m_before["bytes"] - m_after["bytes"]
    byte_pct = (byte_diff / m_before["bytes"] * 100) if m_before["bytes"] else 0

    tok_diff = m_before["tokens"] - m_after["tokens"]
    tok_pct = (tok_diff / m_before["tokens"] * 100) if m_before["tokens"] else 0

    print("=" * 60)
    print(f"Token Compression Report")
    print(f"Before: {before_path}")
    print(f"After:  {after_path}")
    print("=" * 60)
    print(f"{'Metric':<12} | {'Before':<10} | {'After':<10} | {'Saved':<10} | {'Reduction':<10}")
    print("-" * 60)
    print(f"{'Lines':<12} | {m_before['lines']:<10,} | {m_after['lines']:<10,} | {line_diff:<10,} | {line_pct:>6.1f}%")
    print(f"{'Bytes':<12} | {m_before['bytes']:<10,} | {m_after['bytes']:<10,} | {byte_diff:<10,} | {byte_pct:>6.1f}%")
    print(f"{'Tokens':<12} | {m_before['tokens']:<10,} | {m_after['tokens']:<10,} | {tok_diff:<10,} | {tok_pct:>6.1f}%")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure and verify token compression for prompts and skill files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    measure_parser = subparsers.add_parser("measure", help="Measure metrics for a single file.")
    measure_parser.add_argument("--file", "-f", required=True, help="Path to target file.")

    diff_parser = subparsers.add_parser("diff", help="Compare metrics between before and after files.")
    diff_parser.add_argument("--before", "-b", required=True, help="Path to original file.")
    diff_parser.add_argument("--after", "-a", required=True, help="Path to compressed file.")

    args = parser.parse_args()
    if args.command == "measure":
        cmd_measure(args.file)
    elif args.command == "diff":
        cmd_diff(args.before, args.after)


if __name__ == "__main__":
    main()
