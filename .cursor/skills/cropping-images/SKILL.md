---
name: cropping-images
description: Crops a folder of screenshots to the visible video frame and writes numbered JPG outputs plus meta-data.json. Use when the user has local screenshots and wants dataset-style image cleanup.
---

# Cropping Images

## Use This Skill When

Apply this skill when the user already has local images in one folder and wants:

- visible-frame-only crops
- `1.jpg` to `5.jpg`
- `meta-data.json`
- optional deletion of the original screenshots

## Command

```bash
python3 src/crop_images.py --folder ppc/1402 --movie "Jalsa"
```

Add `--keep-originals` when the original screenshots should stay in the folder.

## Validation

- Confirm the folder exists.
- Confirm there are exactly 5 source screenshots.
- Ensure the top title/header UI is gone.
- Ensure the bottom controls and red seek bar are gone.
- Ensure `meta-data.json` exists and keeps blank contributor fields.
