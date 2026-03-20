import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from process_bw_folder import process_black_and_white_folder  # noqa: E402


class ProcessBlackAndWhiteFolderTests(unittest.TestCase):
    @patch("process_bw_folder.colorize_folder")
    @patch("process_bw_folder.crop_folder")
    def test_process_black_and_white_folder_overwrites_cropped_files(
        self,
        mock_crop_folder,
        mock_colorize_folder,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            mock_colorize_folder.return_value = [folder / "1.jpg"]

            written = process_black_and_white_folder(
                folder,
                "Jalsa",
                keep_originals=True,
                preserve_black_and_white=False,
            )

            mock_crop_folder.assert_called_once_with(folder, "Jalsa", keep_originals=True)
            _, kwargs = mock_colorize_folder.call_args
            self.assertEqual(kwargs["output_dir"], folder)
            self.assertTrue(kwargs["overwrite"])
            self.assertEqual(len(kwargs["source_paths"]), 5)
            self.assertEqual(written, [folder / "1.jpg"])

    @patch("process_bw_folder.colorize_folder")
    @patch("process_bw_folder.crop_folder")
    def test_process_black_and_white_folder_can_preserve_bw_outputs(
        self,
        mock_crop_folder,
        mock_colorize_folder,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            mock_colorize_folder.return_value = [folder / "colorized" / "1-colorized.jpg"]

            written = process_black_and_white_folder(
                folder,
                "Jalsa",
                keep_originals=False,
                preserve_black_and_white=True,
            )

            mock_crop_folder.assert_called_once_with(folder, "Jalsa", keep_originals=False)
            _, kwargs = mock_colorize_folder.call_args
            self.assertEqual(kwargs["output_dir"], folder / "colorized")
            self.assertFalse(kwargs["overwrite"])
            self.assertEqual(written, [folder / "colorized" / "1-colorized.jpg"])


if __name__ == "__main__":
    unittest.main()
