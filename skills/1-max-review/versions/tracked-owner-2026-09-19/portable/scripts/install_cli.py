#!/usr/bin/env python3
"""Install a launcher for the copy of max_review.py beside this installer."""

import argparse
import os
from pathlib import Path
import shlex
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bin-dir", type=Path, default=Path.home() / ".local/bin")
    args = parser.parse_args()
    script = Path(__file__).resolve().with_name("max_review.py")
    if not script.is_file():
        parser.error(f"CLI script missing: {script}")
    target = args.bin_dir.expanduser().resolve() / "max-review"
    marker = "# Installed by 1-max-review/scripts/install_cli.py"
    if target.exists() or target.is_symlink():
        if target.is_symlink() or marker not in target.read_text():
            parser.error(f"Refusing to replace another command: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    content = (
        f"#!/bin/sh\n{marker}\n"
        f"exec {shlex.quote(sys.executable)} {shlex.quote(str(script))} \"$@\"\n"
    )
    temporary = target.with_name(f".max-review-install-{os.getpid()}")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.chmod(0o755)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    print(target)
    if str(target.parent) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"Add {target.parent} to PATH, or invoke the printed absolute path.", file=sys.stderr)


if __name__ == "__main__":
    main()
