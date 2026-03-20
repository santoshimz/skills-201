# Skills 201: Image Workflow Composition

[Python 3.10+](https://www.python.org/downloads/)
[License: MIT](./LICENSE)

`skills-201` builds on the `Skills 101` cropping example by composing multiple reusable skills into one workflow.

This project demonstrates three practical layers:

- `cropping-images`: crop screenshots to the visible video frame
- `colorize-images`: colorize black and white images with the Gemini image API
- `process-bw-folder`: run crop first, then colorize the results

## Project Anatomy

- `.agents/skills/.../SKILL.md` explains when each skill should be used
- `.cursor/skills/.../SKILL.md` makes the same skills easy to reuse in Cursor projects
- `src/crop_images.py` handles the local crop workflow
- `src/colorize_images.py` handles Gemini-powered image colorization
- `src/process_bw_folder.py` composes the two skills into one CLI
- `requirements.txt` lists the runtime dependencies
- `pyproject.toml` makes the workflows installable as CLIs

## Quick Start

### Install

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -e ".[dev]"
```

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

### Configure Gemini

Create a `.env` file in the repo root:

```dotenv
GEMINI_API_KEY=your_api_key_here
GEMINI_IMAGE_MODEL=gemini-3.1-flash-image-preview
```

`src/colorize_images.py` and `src/process_bw_folder.py` automatically read `GEMINI_API_KEY` from the environment, an explicit `--env-file`, `.env` in the current working directory, or `.env` in the repo root.

The default image model is `gemini-3.1-flash-image-preview`, the current Gemini 3.1 Flash Image preview model.

## Example Workflows

Crop only:

```bash
python3 src/crop_images.py --folder examples --movie "Movie Title" --keep-originals
```

Colorize existing images into a separate folder:

```bash
python3 src/colorize_images.py --folder examples --output-dir examples/colorized
```

Run crop and then colorize in place:

```bash
python3 src/process_bw_folder.py --folder examples --movie "Movie Title" --keep-originals
```

Preserve the black and white cropped files and write colored copies to `colorized/`:

```bash
python3 src/process_bw_folder.py --folder examples --movie "Movie Title" --keep-originals --preserve-black-and-white
```

## Skill Usage

If this is used as an agent skill, the user does not need to know the Python command.

They can simply say:

```text
Crop and colorize the image in `examples/black and white.png`, and save the outputs next to the original.
```

Other valid styles:

```text
Take the black and white image in `examples/black and white.png`, crop it to the portrait only, then create a colorized version.
```

```text
colorize-image
path: examples/black and white.png
save-next-to-original: true
```

For crop-only requests:

```text
Crop the image in `examples/black and white.png` so the portrait is the focus and save a cropped copy.
```

For colorize-only requests:

```text
Colorize the black and white image in `examples/black and white.png` and save the output next to the original.
```

For folder-based workflows:

```text
Use the images in `examples` as the source folder, apply the crop workflow, then colorize the results and keep the originals.
```

This is the main `Skills 201` idea:

- The user speaks naturally
- The skills know the rules
- The output stays consistent

## Security Notes

- Never commit `.env`.
- This repo includes `.env.example` only.
- The Gemini client fails closed when `GEMINI_API_KEY` is missing.
- The code never prints raw auth headers or API keys.
- Tests mock Gemini responses and do not make live API calls.

## Run Quality Checks

#### macOS / Linux

```bash
python3 -m ruff check .
python3 -m unittest discover -s tests -v
```

#### Windows PowerShell

```powershell
python -m ruff check .
python -m unittest discover -s tests -v
```

## Reusable Skills

This repo also includes reusable skills for flat Python CLI repo structure, fixture-based `unittest` patterns, and secure Gemini image client integration.
