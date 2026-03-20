# Contributing

Thanks for contributing to `skills-201-image-workflows`.

## Local Setup

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -e ".[dev]"
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

## Before Opening A PR

```bash
python3 -m unittest discover -s tests -v
python3 -m ruff check .
```

- Keep changes focused and testable.
- Add or update tests when behavior changes.
- Update `README.md` when workflow usage changes.
- Do not commit `.env` or API keys.
- Prefer mocked Gemini responses in automated tests.
