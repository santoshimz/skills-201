import os
import subprocess
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPT_PATH = SRC / "colorize_images.py"

sys.path.insert(0, str(SRC))

from colorize_images import colorize_folder, colorize_image, resolve_gemini_api_key  # noqa: E402


def make_png_bytes(color: tuple[int, int, int]) -> bytes:
    with BytesIO() as buffer:
        Image.new("RGB", (12, 12), color).save(buffer, format="PNG")
        return buffer.getvalue()


class FakeInlineData:
    def __init__(self, data: bytes, mime_type: str = "image/png") -> None:
        self.data = data
        self.mime_type = mime_type


class FakePart:
    def __init__(self, *, text: str | None = None, inline_data: FakeInlineData | None = None) -> None:
        self.text = text
        self.inline_data = inline_data


class FakeContent:
    def __init__(self, parts: list[FakePart]) -> None:
        self.parts = parts


class FakeCandidate:
    def __init__(self, parts: list[FakePart]) -> None:
        self.content = FakeContent(parts)


class FakeResponse:
    def __init__(self, parts: list[FakePart]) -> None:
        self.candidates = [FakeCandidate(parts)]


class FakeModels:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate_content(self, *, model: str, contents: list[object]):
        self.calls.append({"model": model, "contents": contents})
        return self.response


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.models = FakeModels(response)


class ColorizeImagesTests(unittest.TestCase):
    def make_source_image(self, folder: Path, name: str = "1.jpg") -> Path:
        path = folder / name
        Image.new("RGB", (20, 20), (120, 120, 120)).save(path, format="JPEG")
        return path

    def test_resolve_gemini_api_key_reads_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")

            self.assertEqual(resolve_gemini_api_key(env_path=env_path), "test-key")

    def test_colorize_image_writes_output_with_mock_client(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source_path = self.make_source_image(folder)
            output_path = folder / "1-colorized.jpg"
            response = FakeResponse([
                FakePart(inline_data=FakeInlineData(make_png_bytes((10, 120, 200))))
            ])
            client = FakeClient(response)

            colorize_image(
                source_path,
                output_path,
                client=client,
                api_key="test-key",
                model="gemini-test-image",
            )

            self.assertTrue(output_path.exists())
            self.assertEqual(client.models.calls[0]["model"], "gemini-test-image")
            with Image.open(output_path) as image:
                self.assertEqual(image.mode, "RGB")

    def test_colorize_folder_writes_to_separate_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            output_dir = folder / "colorized"
            self.make_source_image(folder, "1.jpg")
            self.make_source_image(folder, "2.jpg")
            response = FakeResponse([
                FakePart(inline_data=FakeInlineData(make_png_bytes((25, 50, 200))))
            ])
            client = FakeClient(response)

            written = colorize_folder(
                folder,
                output_dir=output_dir,
                overwrite=False,
                client=client,
                api_key="test-key",
            )

            self.assertEqual(len(written), 2)
            self.assertEqual(written[0].name, "1-colorized.jpg")
            self.assertEqual(written[1].name, "2-colorized.jpg")
            self.assertTrue((output_dir / "1-colorized.jpg").exists())
            self.assertTrue((output_dir / "2-colorized.jpg").exists())

    def test_cli_reports_missing_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            env_path = folder / "missing.env"
            self.make_source_image(folder)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--folder",
                    str(folder),
                    "--overwrite",
                    "--env-file",
                    str(env_path),
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                check=False,
                env={k: v for k, v in os.environ.items() if k not in {"GEMINI_API_KEY", "GEMINI_IMAGE_MODEL"}},
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing GEMINI_API_KEY", result.stderr)


if __name__ == "__main__":
    unittest.main()
