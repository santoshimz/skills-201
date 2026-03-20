import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FIXTURE_IMAGE = ROOT / "examples" / "black and white.png"
SCRIPT_PATH = SRC / "crop_images.py"

sys.path.insert(0, str(SRC))

from crop_images import process_folder  # noqa: E402


class CropImagesTests(unittest.TestCase):
    def copy_examples(self, target_dir: Path, count: int = 5) -> list[Path]:
        copied_files: list[Path] = []
        for index in range(1, count + 1):
            destination = target_dir / f"Screenshot {index}.png"
            shutil.copy2(FIXTURE_IMAGE, destination)
            copied_files.append(destination)
        self.assertEqual(len(copied_files), count)
        return copied_files

    def test_process_folder_creates_outputs_and_deletes_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            original_files = self.copy_examples(folder, count=3)

            written = process_folder(folder, keep_originals=False)

            self.assertEqual([path.name for path in written], [
                "Screenshot 1-cropped.jpg",
                "Screenshot 2-cropped.jpg",
                "Screenshot 3-cropped.jpg",
            ])
            for path in written:
                self.assertTrue(path.exists())
            for path in original_files:
                self.assertFalse(path.exists())

    def test_process_folder_keep_originals_preserves_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            original_files = self.copy_examples(folder, count=2)

            written = process_folder(folder, keep_originals=True)

            self.assertEqual(len(written), 2)
            for path in written:
                self.assertTrue(path.exists())
            for path in original_files:
                self.assertTrue(path.exists())

    def test_cli_script_runs_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self.copy_examples(folder, count=3)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--folder",
                    str(folder),
                    "--keep-originals",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertIn("Processed folder:", result.stdout)

    def test_process_folder_rejects_missing_folder(self) -> None:
        missing = ROOT / "does-not-exist"
        with self.assertRaises(FileNotFoundError):
            process_folder(missing, keep_originals=False)

    def test_process_folder_rejects_when_no_source_images_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            (folder / "ignore-cropped.jpg").write_bytes(b"not-an-image")

            with self.assertRaises(RuntimeError) as context:
                process_folder(folder, keep_originals=False)

            self.assertIn("No source images found", str(context.exception))

    def test_cli_script_returns_error_for_missing_folder(self) -> None:
        missing = ROOT / "does-not-exist"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--folder",
                str(missing),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
