import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from process_bw_images import process_black_and_white_images  # noqa: E402


class ProcessBlackAndWhiteImagesTests(unittest.TestCase):
    @patch("process_bw_images.colorize_folder")
    @patch("process_bw_images.crop_folder")
    def test_process_black_and_white_images_overwrites_cropped_files(
        self,
        mock_crop_folder,
        mock_colorize_folder,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            cropped_paths = [folder / "scene-cropped.jpg"]
            mock_crop_folder.return_value = cropped_paths
            mock_colorize_folder.return_value = cropped_paths

            written = process_black_and_white_images(
                folder,
                keep_originals=True,
                preserve_black_and_white=False,
            )

            mock_crop_folder.assert_called_once_with(folder, keep_originals=True)
            _, kwargs = mock_colorize_folder.call_args
            self.assertEqual(kwargs["output_dir"], folder)
            self.assertTrue(kwargs["overwrite"])
            self.assertEqual(kwargs["source_paths"], cropped_paths)
            self.assertEqual(written, cropped_paths)

    @patch("process_bw_images.colorize_folder")
    @patch("process_bw_images.crop_folder")
    def test_process_black_and_white_images_can_preserve_bw_outputs(
        self,
        mock_crop_folder,
        mock_colorize_folder,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            cropped_paths = [folder / "scene-cropped.jpg"]
            mock_crop_folder.return_value = cropped_paths
            mock_colorize_folder.return_value = [folder / "colorized" / "scene-cropped-colorized.jpg"]

            written = process_black_and_white_images(
                folder,
                keep_originals=False,
                preserve_black_and_white=True,
            )

            mock_crop_folder.assert_called_once_with(folder, keep_originals=False)
            _, kwargs = mock_colorize_folder.call_args
            self.assertEqual(kwargs["output_dir"], folder / "colorized")
            self.assertFalse(kwargs["overwrite"])
            self.assertEqual(kwargs["source_paths"], cropped_paths)
            self.assertEqual(written, [folder / "colorized" / "scene-cropped-colorized.jpg"])


if __name__ == "__main__":
    unittest.main()
