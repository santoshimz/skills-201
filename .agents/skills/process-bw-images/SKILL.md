---
name: process-bw-images
description: Runs the crop workflow first and then colorizes the cropped images with Gemini. Use when the user wants one or more black and white images in a folder processed end-to-end.
---

# Process Black And White Images

## Use This Skill When

Apply this skill when one request should do both tasks for images in a folder:

1. crop to the visible image frame
2. colorize the cropped outputs

## Workflow

This is a meta-skill. Do not jump straight to `src/process_bw_images.py` when the point is to demonstrate multi-skill composition.

Instead:

1. Apply the `cropping-images` skill to create `*-cropped.jpg` files from the source images.
2. Apply the `colorize-images` skill only to the cropped outputs.

## Commands

Keep the original source images, then colorize only the cropped JPGs into `colorized/`:

```bash
python3 src/crop_images.py --folder examples --keep-originals
python3 src/colorize_images.py --folder examples --glob "*-cropped.jpg" --output-dir examples/colorized
```

Replace the cropped JPGs with colorized versions after the crop step:

```bash
python3 src/crop_images.py --folder examples --keep-originals
python3 src/colorize_images.py --folder examples --glob "*-cropped.jpg" --overwrite
```

`src/process_bw_images.py` is a legacy convenience wrapper for non-skill usage. Prefer this skill composition path.

## Validation

- The crop step must finish successfully before colorization starts.
- If the user wants safety, keep originals or preserve black and white outputs.
- Verify the cropped and colorized output files exist for each processed source image.
