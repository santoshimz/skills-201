---
name: python-secure-gemini-image-client
description: Integrates Gemini image editing securely in Python CLIs with .env loading, secret-safe error handling, and mockable client boundaries. Use when wiring Gemini image generation or editing into local Python tools.
---

# Python Secure Gemini Image Client

## Security Rules

- Read `GEMINI_API_KEY` from the environment or `.env`.
- Never hardcode keys.
- Never print raw auth headers or keys.
- Keep the Gemini client behind a helper so tests can inject a fake client.
- Prefer stable model names unless the user explicitly wants a preview model.

## Implementation Pattern

- Resolve secrets first.
- Resolve the model name next.
- Create the real Gemini client only when needed.
- Extract image bytes from the response into a save helper.
- Raise clear errors when Gemini returns text but no image.
