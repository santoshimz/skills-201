---
name: python-unittest-fixtures
description: Builds fixture-based unittest coverage for flat Python CLIs, including temporary directories, subprocess CLI checks, and mock-backed API tests. Use when adding Python tests to repos like skills101 or skills201.
---

# Python Unittest Fixtures

## Preferred Test Pattern

- Keep small committed fixtures under `examples/`
- Copy fixtures into `tempfile.TemporaryDirectory()` during tests
- Test the imported workflow function directly
- Add at least one subprocess-based CLI smoke test
- Mock network clients instead of calling live services

## Validation Targets

- success path
- missing input path
- invalid input count or shape
- CLI error handling
- mocked remote response handling
