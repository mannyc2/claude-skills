#!/usr/bin/env python3
"""
Search tempoxyz/tempo docs/pages by downloading the repo as a zip and grepping locally.

Examples:
  python search_repo.py "transaction spec"
  python search_repo.py "TempoTransaction" --regex --ignore-case
  python search_repo.py "fee sponsor" --context 2 --include "*.md,*.mdx"
  python search_repo.py "x402" --repo tempoxyz/tempo --ref main --path docs/pages
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional, Sequence, Tuple

import requests


@dataclass(frozen=True)
class Match:
    file: Path
    line_no: int
    col: int
    line: str


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("query", help="Text to search for (substring) unless --regex is set")
    p.add_argument("--repo", default="tempoxyz/tempo", help='GitHub "owner/repo" (default: tempoxyz/tempo)')
    p.add_argument("--ref", default="main", help='Branch/tag/sha (default: "main")')
    p.add_argument("--path", default="docs/pages", help='Subdirectory to search (default: "docs/pages")')
    p.add_argument("--regex", action="store_true", help="Treat query as a regular expression")
    p.add_argument("--ignore-case", action="store_true", help="Case-insensitive search")
    p.add_argument("--context", type=int, default=0, help="Print N context lines before/after each match")
    p.add_argument(
        "--include",
        default="*",
        help='Comma-separated glob patterns to include (default: "*"). Example: "*.md,*.mdx,*.tsx"',
    )
    p.add_argument("--max-matches", type=int, default=0, help="Stop after N matches (0 = unlimited)")
    p.add_argument("--timeout", type=float, default=60.0, help="HTTP timeout seconds (default: 60)")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color")
    return p.parse_args(argv)


def github_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-search-script",
    }
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def download_repo_zip(repo: str, ref: str, timeout: float) -> Path:
    url = f"https://api.github.com/repos/{repo}/zipball/{ref}"
    with requests.get(url, headers=github_headers(), stream=True, timeout=timeout) as r:
        if r.status_code >= 400:
            msg = r.text.strip()[:2000]
            raise RuntimeError(f"GitHub download failed: HTTP {r.status_code}\n{msg}")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        try:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    tmp.write(chunk)
            tmp.flush()
            return Path(tmp.name)
        finally:
            tmp.close()


def extract_zip(zip_path: Path) -> Path:
    out_dir = Path(tempfile.mkdtemp(prefix="repo_search_"))
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)

    # GitHub zipball contains a single top-level folder like owner-repo-sha/
    children = [p for p in out_dir.iterdir() if p.is_dir()]
    if len(children) == 1:
        return children[0]
    return out_dir


def iter_files(root: Path, rel_path: str, include_globs: Sequence[str]) -> Iterator[Path]:
    base = root / rel_path
    if not base.exists():
        raise FileNotFoundError(f"Path not found in repo: {rel_path}")

    for p in base.rglob("*"):
        if not p.is_file():
            continue
        name = p.name
        if include_globs != ["*"] and not any(fnmatch.fnmatch(name, g) for g in include_globs):
            continue
        yield p


def build_matcher(query: str, regex: bool, ignore_case: bool):
    if regex:
        flags = re.MULTILINE
        if ignore_case:
            flags |= re.IGNORECASE
        rx = re.compile(query, flags)

        def find_in_line(line: str) -> Optional[Tuple[int, int]]:
            m = rx.search(line)
            if not m:
                return None
            return (m.start(), m.end())

        return find_in_line
    else:
        needle = query.lower() if ignore_case else query

        def find_in_line(line: str) -> Optional[Tuple[int, int]]:
            hay = line.lower() if ignore_case else line
            idx = hay.find(needle)
            if idx == -1:
                return None
            return (idx, idx + len(needle))

        return find_in_line


def colorize(s: str, code: str, enabled: bool) -> str:
    if not enabled:
        return s
    return f"\x1b[{code}m{s}\x1b[0m"


def search_file(path: Path, find_in_line, max_matches: int) -> Iterator[Match]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return

    for i, line in enumerate(text.splitlines(), start=1):
        span = find_in_line(line)
        if not span:
            continue
        col = span[0] + 1
        yield Match(file=path, line_no=i, col=col, line=line)
        if max_matches and max_matches <= 1:
            return
        if max_matches:
            max_matches -= 1


def print_match_with_context(
    match: Match,
    root: Path,
    context: int,
    find_in_line,
    color: bool,
) -> None:
    rel = match.file.relative_to(root)
    header = f"{rel}:{match.line_no}:{match.col}"
    print(colorize(header, "36", color))

    lines = match.file.read_text(encoding="utf-8", errors="replace").splitlines()
    i = match.line_no - 1
    lo = max(0, i - context)
    hi = min(len(lines), i + context + 1)

    for j in range(lo, hi):
        prefix = ">" if j == i else " "
        ln = f"{j+1}".rjust(len(str(hi)))
        line = lines[j]

        # highlight first occurrence on the matching line
        if j == i:
            span = find_in_line(line)
            if span:
                a, b = span
                line = (
                    line[:a]
                    + colorize(line[a:b], "31", color)  # red
                    + line[b:]
                )

        print(f" {prefix} {ln} | {line}")
    print()


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    include_globs = [g.strip() for g in args.include.split(",") if g.strip()]
    if not include_globs:
        include_globs = ["*"]

    use_color = (not args.no_color) and sys.stdout.isatty()

    zip_path = None
    try:
        zip_path = download_repo_zip(args.repo, args.ref, args.timeout)
        repo_root = extract_zip(zip_path)

        find_in_line = build_matcher(args.query, args.regex, args.ignore_case)

        total = 0
        for f in iter_files(repo_root, args.path, include_globs):
            remaining = 0 if args.max_matches == 0 else (args.max_matches - total)
            if args.max_matches and remaining <= 0:
                break

            for m in search_file(f, find_in_line, remaining if args.max_matches else 0):
                print_match_with_context(m, repo_root, args.context, find_in_line, use_color)
                total += 1
                if args.max_matches and total >= args.max_matches:
                    break

        if total == 0:
            print("No matches found.")
            return 1

        print(f"Matches: {total}")
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    finally:
        if zip_path and zip_path.exists():
            try:
                zip_path.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
