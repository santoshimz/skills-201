---
name: python-flat-cli-repo
description: Scaffolds a flat Python CLI repository modeled after small workflow repos with root-level modules, pyproject scripts, tests, and lightweight tooling. Use when building a reusable Python workflow repo similar to skills101 or skills201.
---

# Python Flat CLI Repo

## Pattern

Use this repo shape:

- flat workflow modules under `src/` such as `src/crop_images.py`
- `pyproject.toml` with `[project.scripts]`
- `requirements.txt` for runtime installs
- `tests/` using `unittest`
- `.github/workflows/ci.yml` running lint and tests

## Guidelines

- Keep `main()` thin.
- Put reusable logic in functions that tests can import directly.
- Prefer `pathlib` for cross-platform behavior.
- Keep dependencies minimal.
