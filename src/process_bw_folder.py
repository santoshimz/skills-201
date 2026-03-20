#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from colorize_images import DEFAULT_IMAGE_MODEL, DEFAULT_PROMPT, colorize_folder
from crop_images import process_folder as crop_folder


def process_black_and_white_folder(
    folder: Path,
    movie_name: str,
    *,
    keep_originals: bool,
    preserve_black_and_white: bool,
    prompt: str = DEFAULT_PROMPT,
    model: str | None = None,
    env_path: Path | None = None,
) -> list[Path]:
    crop_folder(folder, movie_name, keep_originals=keep_originals)
    source_paths = [folder / f"{index}.jpg" for index in range(1, 6)]
    output_dir = folder / "colorized" if preserve_black_and_white else folder
    overwrite = not preserve_black_and_white
    return colorize_folder(
        folder,
        output_dir=output_dir,
        overwrite=overwrite,
        prompt=prompt,
        model=model or DEFAULT_IMAGE_MODEL,
        env_path=env_path,
        source_paths=source_paths,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Crop a folder of screenshots and colorize the resulting images with Gemini."
    )
    parser.add_argument("--folder", required=True, type=Path, help="Folder containing source screenshots.")
    parser.add_argument("--movie", required=True, help="Movie title to store in meta-data.json.")
    parser.add_argument(
        "--keep-originals",
        action="store_true",
        help="Keep the original screenshots after cropping succeeds.",
    )
    parser.add_argument(
        "--preserve-black-and-white",
        action="store_true",
        help="Write colorized outputs to a colorized/ subfolder instead of replacing the cropped JPGs.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Editing instruction sent to Gemini.",
    )
    parser.add_argument(
        "--model",
        help="Override the Gemini image model. Defaults to GEMINI_IMAGE_MODEL or gemini-3.1-flash-image-preview.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional path to a .env file containing GEMINI_API_KEY.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        folder = args.folder.expanduser().resolve()
        env_path = args.env_file.expanduser().resolve() if args.env_file else None
        written_paths = process_black_and_white_folder(
            folder,
            args.movie,
            keep_originals=args.keep_originals,
            preserve_black_and_white=args.preserve_black_and_white,
            prompt=args.prompt,
            model=args.model,
            env_path=env_path,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Processed and colorized folder: {folder}")
    print("Created files: " + ", ".join(path.relative_to(folder).as_posix() for path in written_paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
