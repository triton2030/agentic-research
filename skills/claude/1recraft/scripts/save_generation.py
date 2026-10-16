#!/usr/bin/env python3
"""Persist Recraft outputs and their exact prompt in the current project."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Save Recraft outputs under _workspace/design/recraft-images."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        required=True,
        help="Absolute root of the active project/workspace.",
    )
    parser.add_argument("--name", required=True, help="Readable image name.")
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Local path or HTTP(S) output URL; repeat for multiple outputs.",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Exact prompt or prompt-less operation instruction for the .md pair.",
    )
    parser.add_argument(
        "--date",
        dest="generation_date",
        type=date.fromisoformat,
        default=datetime.now().astimezone().date(),
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    slug = re.sub(r"[^\w]+", "-", normalized, flags=re.UNICODE).strip("-_")
    if not slug:
        raise ValueError("--name must contain at least one letter or number")
    return slug


def day_directory(project_root: Path, generation_date: date) -> Path:
    folder = generation_date.strftime("%m-%d")
    destination = (
        project_root.resolve() / "_workspace" / "design" / "recraft-images" / folder
    )
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def next_basename(destination: Path, requested: str) -> str:
    candidate = requested
    revision = 2
    while any(destination.glob(f"{candidate}.*")):
        candidate = f"{requested}-{revision}"
        revision += 1
    return candidate


def download_source(source: str, temp_directory: Path) -> tuple[Path, str | None]:
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = urllib.request.Request(
            source, headers={"User-Agent": "recraft-images/1"}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            content_type = response.headers.get_content_type()
            suffix = (
                Path(parsed.path).suffix
                or mimetypes.guess_extension(content_type)
                or ""
            )
            target = temp_directory / f"download{suffix}"
            with target.open("wb") as output:
                shutil.copyfileobj(response, output)
        return target, content_type

    if parsed.scheme == "file":
        path = Path(urllib.request.url2pathname(parsed.path))
    elif parsed.scheme:
        raise ValueError(f"unsupported source scheme: {parsed.scheme}")
    else:
        path = Path(source).expanduser()

    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"source does not exist: {resolved}")
    return resolved, mimetypes.guess_type(resolved.name)[0]


def is_svg(source: Path, content_type: str | None) -> bool:
    if content_type == "image/svg+xml" or source.suffix.lower() == ".svg":
        return True
    with source.open("rb") as input_file:
        head = input_file.read(4096).lstrip()
    return b"<svg" in head.lower()


def is_png(source: Path, content_type: str | None) -> bool:
    if content_type == "image/png":
        return True
    with source.open("rb") as input_file:
        return input_file.read(8) == b"\x89PNG\r\n\x1a\n"


def convert_to_png(source: Path, destination: Path) -> None:
    sips = Path("/usr/bin/sips")
    if not sips.is_file():
        raise RuntimeError(
            "/usr/bin/sips is required to normalize raster output to PNG"
        )
    result = subprocess.run(
        [str(sips), "-s", "format", "png", str(source), "--out", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not destination.is_file():
        detail = (
            result.stderr.strip() or result.stdout.strip() or "unknown conversion error"
        )
        raise RuntimeError(f"could not convert raster output to PNG: {detail}")


def persist_one(
    source_value: str,
    destination: Path,
    basename: str,
    prompt: str,
) -> tuple[Path, Path]:
    with tempfile.TemporaryDirectory(prefix="recraft-save-") as temp_name:
        temp_directory = Path(temp_name)
        source, content_type = download_source(source_value, temp_directory)
        extension = ".svg" if is_svg(source, content_type) else ".png"
        image_path = destination / f"{basename}{extension}"
        prompt_path = destination / f"{basename}.md"
        temp_image = destination / f".{basename}{extension}.tmp"
        temp_prompt = destination / f".{basename}.md.tmp"

        try:
            if extension == ".svg" or is_png(source, content_type):
                shutil.copyfile(source, temp_image)
            else:
                convert_to_png(source, temp_image)
            temp_prompt.write_text(prompt, encoding="utf-8")
            os.replace(temp_image, image_path)
            os.replace(temp_prompt, prompt_path)
        except Exception:
            temp_image.unlink(missing_ok=True)
            temp_prompt.unlink(missing_ok=True)
            image_path.unlink(missing_ok=True)
            prompt_path.unlink(missing_ok=True)
            raise

    return image_path, prompt_path


def main() -> int:
    args = parse_args()
    if not args.prompt.strip():
        raise ValueError("--prompt must not be empty")
    destination = day_directory(args.project_root, args.generation_date)
    root_name = slugify(args.name)
    multiple = len(args.source) > 1
    saved: list[dict[str, str]] = []

    for index, source in enumerate(args.source, start=1):
        requested = f"{root_name}-{index:02d}" if multiple else root_name
        basename = next_basename(destination, requested)
        image_path, prompt_path = persist_one(
            source,
            destination,
            basename,
            args.prompt,
        )
        saved.append(
            {
                "image": str(image_path.resolve()),
                "prompt": str(prompt_path.resolve()),
            }
        )

    print(json.dumps({"saved": saved}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
