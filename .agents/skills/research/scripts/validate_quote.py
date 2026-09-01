"""
CLI utility to validate that quotes and extracted phrases exist verbatim in source material.
Uses regex with whitespace normalization to match exact word sequences across single files or directories.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def normalize_whitespace(text: str) -> str:
    """Collapses consecutive whitespace and linebreaks into single spaces for robust matching."""
    return re.sub(r"\s+", " ", text).strip()


def build_quote_pattern(quote: str, case_sensitive: bool = True) -> re.Pattern[str]:
    """
    Builds a regex pattern where arbitrary whitespace in the source matches any whitespace in the quote.
    Escapes special regex characters in individual words.
    """
    words = quote.strip().split()
    if not words:
        raise ValueError("Quote string cannot be empty.")
    
    escaped_words = [re.escape(w) for w in words]
    # Allow any whitespace sequence (spaces, tabs, newlines) between words
    pattern_str = r"\s+".join(escaped_words)
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(pattern_str, flags)


def validate_in_file(file_path: Path, quote: str, case_sensitive: bool = True) -> tuple[bool, str, int | None]:
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, f"Failed to read file: {e}", None

    pattern = build_quote_pattern(quote, case_sensitive=case_sensitive)
    match = pattern.search(content)

    if match:
        start_idx = match.start()
        # Find line number
        line_num = content[:start_idx].count("\n") + 1
        # Extract surrounding context snippet (up to 120 chars around match)
        snippet_start = max(0, start_idx - 60)
        snippet_end = min(len(content), match.end() + 60)
        snippet = content[snippet_start:snippet_end].replace("\n", " ").strip()
        return True, f"...{snippet}...", line_num
    
    return False, "Quote not found in source text.", None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify whether a quote or phrase exists verbatim in source document(s)."
    )
    parser.add_argument(
        "--quote", "-q", required=True, help="The exact quote or phrase to search for."
    )
    parser.add_argument(
        "--file", "-f", help="Path to a single source document (markdown, text, HTML, etc.)."
    )
    parser.add_argument(
        "--dir", "-d", help="Directory of source documents to search across."
    )
    parser.add_argument(
        "--ignore-case", "-i", action="store_true", help="Perform case-insensitive matching."
    )

    args = parser.parse_args()

    if not args.file and not args.dir:
        print("Error: Must provide either --file or --dir", file=sys.stderr)
        sys.exit(2)

    case_sensitive = not args.ignore_case
    quote = args.quote.strip()

    if not quote:
        print("Error: Empty quote provided.", file=sys.stderr)
        sys.exit(2)

    target_files: list[Path] = []
    if args.file:
        p = Path(args.file)
        if not p.is_file():
            print(f"Error: File not found: {p}", file=sys.stderr)
            sys.exit(2)
        target_files.append(p)
    elif args.dir:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"Error: Directory not found: {d}", file=sys.stderr)
            sys.exit(2)
        target_files.extend([f for f in d.rglob("*") if f.is_file()])

    if not target_files:
        print("Error: No valid source files found to search.", file=sys.stderr)
        sys.exit(2)

    found_matches = []
    for f in target_files:
        matched, snippet, line_num = validate_in_file(f, quote, case_sensitive=case_sensitive)
        if matched:
            found_matches.append((f, line_num, snippet))

    if found_matches:
        print(f"[VALIDATED] Quote verified ({len(found_matches)} match{'es' if len(found_matches) > 1 else ''} found):")
        for f, line_num, snippet in found_matches:
            print(f"  Source: {f} (Line {line_num})")
            print(f"  Context: {snippet}")
        sys.exit(0)
    else:
        print(f"[FAILED] Quote not found in {len(target_files)} searched file(s).", file=sys.stderr)
        print(f"  Searched Quote: \"{quote}\"", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
