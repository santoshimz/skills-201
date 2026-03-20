---
name: process-bw-folder
description: Runs the crop workflow first and then colorizes the cropped images with Gemini. Use when the user wants a black and white screenshot folder processed end-to-end.
---

# Process Black And White Folder

## Use This Skill When

Apply this skill when one request should do both tasks:

1. crop to the visible movie frame
2. colorize the cropped outputs

## Command

Replace the cropped JPGs with colored versions:

```bash
python3 src/process_bw_folder.py --folder ppc/1402 --movie "Jalsa"
```

Keep the cropped black and white JPGs and save colored copies under `colorized/`:

```bash
python3 src/process_bw_folder.py --folder ppc/1402 --movie "Jalsa" --preserve-black-and-white
```

## Validation

- The crop step must finish successfully before colorization starts.
- If the user wants safety, keep originals or preserve black and white outputs.
- Verify the expected output files exist after both steps.
