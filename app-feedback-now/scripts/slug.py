"""
Derive a project slug for app-feedback-now.

Order of preference:
  1. Explicit --override <slug>           (caller wants this slug, no questions)
  2. Basename of git remote `origin` URL  (most stable across worktrees & checkouts)
  3. Basename of $PWD                     (any directory, not a repo)

Slugs are lowercased and limited to [a-z0-9._-]; anything else collapses to '-'.
Empty result falls back to 'app'.

Usage:
    python scripts/slug.py [--cwd <path>] [--override <slug>]

Prints the slug to stdout. No newline-terminator subtleties — just a string.
"""
from __future__ import annotations  # `str | None` on Python 3.7+

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


SLUG_OK = re.compile(r"[^a-z0-9._-]+")


def _normalize(s: str) -> str:
    s = (s or "").strip().lower()
    # Strip a trailing .git common in git URLs.
    if s.endswith(".git"):
        s = s[:-4]
    s = SLUG_OK.sub("-", s).strip("-._")
    return s or "app"


def _git_remote_slug(cwd: Path) -> str | None:
    """Try `git config --get remote.origin.url` inside cwd. Returns the
    basename (without .git) or None if not a git repo / no origin."""
    try:
        out = subprocess.run(
            ["git", "-C", str(cwd), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=2,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    url = out.stdout.strip()
    if not url:
        return None
    # Last path segment of the URL, regardless of scheme (https://, git@, etc).
    # Strip query/fragment if any.
    seg = url.rstrip("/").split("/")[-1].split(":")[-1]
    return _normalize(seg)


def derive(cwd: Path, override: str | None = None) -> str:
    if override:
        return _normalize(override)
    git = _git_remote_slug(cwd)
    if git:
        return git
    return _normalize(cwd.name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cwd", default=os.getcwd(),
                    help="Directory to derive the slug from. Defaults to $PWD.")
    ap.add_argument("--override", default=None,
                    help="Use this exact slug (still normalized).")
    args = ap.parse_args()

    sys.stdout.write(derive(Path(args.cwd).resolve(), args.override))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
