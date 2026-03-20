import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FIXTURE_IMAGE = ROOT / "examples" / "ppc" / "1402" / "black and white.png"
SCRIPT_PATH = SRC / "crop_images.py"

sys.path.insert(0, str(SRC))

from crop_images import process_folder  # noqa: E402


class CropImagesTests(unittest.TestCase):
    def copy_examples(self, target_dir: Path) -> list[Path]:
        copied_files: list[Path] = []
        for index in range(1, 6):
            destination = target_dir / f"Screenshot {index}.png"
            shutil.copy2(FIXTURE_IMAGE, destination)
            copied_files.append(destination)
        self.assertEqual(len(copied_files), 5)
        return copied_files

    def test_process_folder_creates_outputs_and_deletes_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            original_files = self.copy_examples(folder)

            process_folder(folder, "Jalsa", keep_originals=False)

            for index in range(1, 6):
                self.assertTrue((folder / f"{index}.jpg").exists())
            self.assertTrue((folder / "meta-data.json").exists())
            for path in original_files:
                self.assertFalse(path.exists())

            metadata = json.loads((folder / "meta-data.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["movie"], "Jalsa")
            self.assertEqual(metadata["contributor"], "")
            self.assertEqual(metadata["twitterId"], "")

    def test_process_folder_keep_originals_preserves_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            original_files = self.copy_examples(folder)

            process_folder(folder, "Jalsa", keep_originals=True)

            for index in range(1, 6):
                self.assertTrue((folder / f"{index}.jpg").exists())
            self.assertTrue((folder / "meta-data.json").exists())
            for path in original_files:
                self.assertTrue(path.exists())

    def test_cli_script_runs_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self.copy_examples(folder)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--folder",
                    str(folder),
                    "--movie",
                    "Jalsa",
                    "--keep-originals",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertIn("Processed folder:", result.stdout)
            self.assertTrue((folder / "meta-data.json").exists())

    def test_process_folder_rejects_missing_folder(self) -> None:
        missing = ROOT / "does-not-exist"
        with self.assertRaises(FileNotFoundError):
            process_folder(missing, "Jalsa", keep_originals=False)

    def test_process_folder_rejects_wrong_image_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            copied = self.copy_examples(folder)
            copied[0].unlink()

            with self.assertRaises(RuntimeError) as context:
                process_folder(folder, "Jalsa", keep_originals=False)

            self.assertIn("Expected exactly 5 source images", str(context.exception))

    def test_cli_script_returns_error_for_missing_folder(self) -> None:
        missing = ROOT / "does-not-exist"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--folder",
                str(missing),
                "--movie",
                "Jalsa",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
