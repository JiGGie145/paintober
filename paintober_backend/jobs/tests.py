import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from .storage import LocalJobStorage


class LocalJobStorageTests(SimpleTestCase):
    def test_round_trips_files_using_relative_keys(self):
        with tempfile.TemporaryDirectory() as media_dir, tempfile.TemporaryDirectory() as work_dir:
            with override_settings(MEDIA_ROOT=Path(media_dir)):
                storage = LocalJobStorage()
                source = Path(work_dir) / "source.png"
                destination = Path(work_dir) / "nested" / "copy.png"
                source.write_bytes(b"png data")

                self.assertEqual(
                    storage.save_upload("jobs/example/input/original.png", source, "image/png"),
                    "jobs/example/input/original.png",
                )
                self.assertTrue(storage.upload_exists("jobs/example/input/original.png"))
                storage.download_upload("jobs/example/input/original.png", destination)
                self.assertEqual(destination.read_bytes(), b"png data")

                storage.delete_upload("jobs/example/input/original.png")
                self.assertFalse(storage.upload_exists("jobs/example/input/original.png"))

    def test_rejects_path_traversal(self):
        with override_settings(MEDIA_ROOT=Path(tempfile.gettempdir())):
            storage = LocalJobStorage()
            with self.assertRaises(ValueError):
                storage.result_exists("../outside.txt")