#!/usr/bin/env python3
"""
Convert a file to Markdown using the local markitdown installation.

Default environment:
- Venv Python: F:/ai_proj/markitdown/.venv/Scripts/python.exe
- Package: markitdown[all] installed in that venv

Override with env vars:
- MARKITDOWN_VENV_PYTHON
- MARKITDOWN_PYTHON_FALLBACK
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_VENV_PYTHON = r"F:\ai_proj\markitdown\.venv\Scripts\python.exe"
DEFAULT_FALLBACK_PYTHON = "python"


def resolve_python() -> str:
    return os.getenv("MARKITDOWN_VENV_PYTHON") or DEFAULT_VENV_PYTHON


def resolve_fallback_python() -> str:
    return os.getenv("MARKITDOWN_PYTHON_FALLBACK") or DEFAULT_FALLBACK_PYTHON


def find_markitdown_command(python_exe: str) -> list[str]:
    candidate = Path(python_exe).with_name("markitdown.exe")
    if candidate.exists():
        return [str(candidate)]
    return [python_exe, "-m", "markitdown"]


def run_convert(input_file: Path, output_file: Path | None, extra_args: list[str], python_exe: str) -> int:
    cmd = find_markitdown_command(python_exe) + [str(input_file)] + extra_args
    if output_file is not None:
        cmd += ["-o", str(output_file)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        if output_file is None:
            sys.stdout.write(result.stdout)
        else:
            print(f"Wrote: {output_file}")
        return 0

    fallback_python = resolve_fallback_python()
    if python_exe != fallback_python:
        cmd = find_markitdown_command(fallback_python) + [str(input_file)] + extra_args
        if output_file is not None:
            cmd += ["-o", str(output_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            if output_file is None:
                sys.stdout.write(result.stdout)
            else:
                print(f"Wrote: {output_file}")
            return 0

    sys.stderr.write(result.stderr or "markitdown failed\n")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert files to Markdown with markitdown.")
    parser.add_argument("input_file", help="Source file to convert.")
    parser.add_argument("-o", "--output", help="Output Markdown file path.")
    parser.add_argument("-x", "--extension", help="Hint about file extension.")
    parser.add_argument("-m", "--mime-type", help="Hint about MIME type.")
    parser.add_argument("-c", "--charset", help="Hint about charset.")
    parser.add_argument("--use-plugins", action="store_true", help="Enable markitdown plugins.")
    parser.add_argument("--keep-data-uris", action="store_true", help="Keep data URIs in output.")
    args = parser.parse_args()

    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"Input file not found: {input_file}", file=sys.stderr)
        return 2

    output_file = Path(args.output) if args.output else None
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)

    extra_args: list[str] = []
    if args.extension:
        extra_args += ["-x", args.extension]
    if args.mime_type:
        extra_args += ["-m", args.mime_type]
    if args.charset:
        extra_args += ["-c", args.charset]
    if args.use_plugins:
        extra_args += ["--use-plugins"]
    if args.keep_data_uris:
        extra_args += ["--keep-data-uris"]

    python_exe = resolve_python()
    return run_convert(input_file, output_file, extra_args, python_exe)


if __name__ == "__main__":
    raise SystemExit(main())
