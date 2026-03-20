---
name: colorize-images
description: Colorizes black and white images with the Gemini image API using GEMINI_API_KEY from .env or the environment. Use when the user wants realistic colorization without changing scene composition.
---

# Colorize Images

## Use This Skill When

Apply this skill when the user wants to turn black and white photos into color images using Gemini.

## Defaults

- Reads `GEMINI_API_KEY` from the environment or `.env`
- Uses `GEMINI_IMAGE_MODEL` when present
- Falls back to `gemini-3.1-flash-image-preview`
- Uses a realism-preserving prompt by default

## Command

Colorize images into a separate folder:

```bash
python3 src/colorize_images.py --folder ppc/1402 --output-dir ppc/1402/colorized
```

Replace the files in place:

```bash
python3 src/colorize_images.py --folder ppc/1402 --overwrite
```

## Guardrails

- Never log API keys.
- Fail clearly when `GEMINI_API_KEY` is missing.
- Keep automated tests mocked instead of calling the live API.
- Preserve framing and scene details unless the user explicitly asks for creative changes.
