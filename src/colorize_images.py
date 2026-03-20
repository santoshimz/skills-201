#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Iterable

from PIL import Image


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_IMAGE_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_PROMPT = (
    "Colorize this black and white photo realistically. Preserve the framing, people, "
    "objects, expressions, and scene details. Do not add or remove anything."
)


def parse_dotenv(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_dotenv_values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return parse_dotenv(path.read_text(encoding="utf-8"))


def candidate_env_paths(env_path: Path | None = None) -> list[Path]:
    if env_path is not None:
        return [env_path.expanduser().resolve()]

    paths: list[Path] = []
    for candidate in [Path.cwd() / ".env", Path(__file__).resolve().parents[1] / ".env"]:
        resolved = candidate.resolve()
        if resolved not in paths:
            paths.append(resolved)
    return paths


def resolve_gemini_api_key(api_key: str | None = None, env_path: Path | None = None) -> str:
    if api_key:
        return api_key

    environment_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if environment_key:
        return environment_key

    for path in candidate_env_paths(env_path):
        values = load_dotenv_values(path)
        file_key = values.get("GEMINI_API_KEY", "").strip()
        if file_key:
            return file_key

    raise RuntimeError(
        "Missing GEMINI_API_KEY. Set it in the environment or add it to a .env file."
    )


def resolve_model_name(model: str | None, env_path: Path | None = None) -> str:
    if model:
        return model
    environment_model = os.environ.get("GEMINI_IMAGE_MODEL", "").strip()
    if environment_model:
        return environment_model
    for path in candidate_env_paths(env_path):
        values = load_dotenv_values(path)
        file_model = values.get("GEMINI_IMAGE_MODEL", "").strip()
        if file_model:
            return file_model
    return DEFAULT_IMAGE_MODEL


def create_default_client(api_key: str):
    from google import genai

    return genai.Client(api_key=api_key)


def list_folder_images(folder: Path) -> list[Path]:
    all_images = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    preferred = [folder / f"{index}.jpg" for index in range(1, 6)]
    numbered = [path for path in preferred if path.exists()]
    if numbered:
        return numbered
    return sorted(
        [path for path in all_images if not path.stem.endswith("-colorized")],
        key=lambda path: path.name.lower(),
    )


def collect_generated_images(response) -> list[tuple[bytes, str]]:
    generated: list[tuple[bytes, str]] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            inline_data = getattr(part, "inline_data", None)
            if inline_data is None:
                continue
            payload = getattr(inline_data, "data", None)
            mime_type = getattr(inline_data, "mime_type", "image/png")
            if payload and str(mime_type).startswith("image/"):
                generated.append((payload, mime_type))
    return generated


def collect_response_text(response) -> str:
    fragments: list[str] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            text = getattr(part, "text", None)
            if text:
                fragments.append(text)
    return "\n".join(fragments).strip()


def make_output_path(source_path: Path, output_dir: Path, overwrite: bool) -> Path:
    if overwrite:
        return output_dir / source_path.name
    return output_dir / f"{source_path.stem}-colorized.jpg"


def save_generated_image(image_bytes: bytes, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(image_bytes)) as image:
        image.convert("RGB").save(output_path, format="JPEG", quality=95, optimize=True)


def colorize_image(
    source_path: Path,
    output_path: Path,
    *,
    prompt: str = DEFAULT_PROMPT,
    model: str | None = None,
    api_key: str | None = None,
    client=None,
    env_path: Path | None = None,
) -> Path:
    if not source_path.exists():
        raise FileNotFoundError(f"Image does not exist: {source_path}")

    active_model = resolve_model_name(model, env_path=env_path)
    active_key = resolve_gemini_api_key(api_key=api_key, env_path=env_path)
    active_client = client or create_default_client(active_key)

    with Image.open(source_path) as image:
        source_image = image.convert("RGB")
        response = active_client.models.generate_content(
            model=active_model,
            contents=[prompt, source_image],
        )

    generated = collect_generated_images(response)
    if not generated:
        response_text = collect_response_text(response)
        detail = f" Response text: {response_text}" if response_text else ""
        raise RuntimeError(f"Gemini response did not include an image.{detail}")

    image_bytes, _mime_type = generated[0]
    save_generated_image(image_bytes, output_path)
    return output_path


def colorize_folder(
    folder: Path,
    *,
    output_dir: Path | None = None,
    overwrite: bool = False,
    prompt: str = DEFAULT_PROMPT,
    model: str | None = None,
    api_key: str | None = None,
    client=None,
    env_path: Path | None = None,
    source_paths: Iterable[Path] | None = None,
) -> list[Path]:
    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder}")

    selected_sources = list(source_paths) if source_paths is not None else list_folder_images(folder)
    if not selected_sources:
        raise RuntimeError("No source images found to colorize.")

    target_dir = output_dir if output_dir is not None else folder
    active_key = resolve_gemini_api_key(api_key=api_key, env_path=env_path)
    active_client = client or create_default_client(active_key)
    active_model = resolve_model_name(model, env_path=env_path)

    written_paths: list[Path] = []
    for source_path in selected_sources:
        output_path = make_output_path(source_path, target_dir, overwrite=overwrite)
        colorize_image(
            source_path,
            output_path,
            prompt=prompt,
            model=active_model,
            api_key=active_key,
            client=active_client,
            env_path=env_path,
        )
        written_paths.append(output_path)

    return written_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Colorize black and white images in a folder with the Gemini image model."
    )
    parser.add_argument(
        "--folder",
        required=True,
        type=Path,
        help="Folder containing images to colorize.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional output directory. Defaults to the source folder.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite filenames in the target directory instead of writing *-colorized.jpg.",
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
        output_dir = args.output_dir.expanduser().resolve() if args.output_dir else None
        env_path = args.env_file.expanduser().resolve() if args.env_file else None
        written_paths = colorize_folder(
            folder,
            output_dir=output_dir,
            overwrite=args.overwrite,
            prompt=args.prompt,
            model=args.model,
            env_path=env_path,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Colorized folder: {args.folder.expanduser().resolve()}")
    print("Created files: " + ", ".join(path.name for path in written_paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
