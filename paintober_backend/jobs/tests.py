import base64
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings

from .serializers import JobCreateSerializer
from .storage import LocalJobStorage


class JobCreateSerializerTests(SimpleTestCase):
    image = SimpleUploadedFile(
        "input.png",
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
            "+A8AAQUBAScY42YAAAAASUVORK5CYII="
        ),
        content_type="image/png",
    )

    def serialize(self, **kwargs):
        data = {"image": self.image, **kwargs}
        return JobCreateSerializer(data=data)

    @override_settings(VERTEX_AI_ENABLED=False)
    def test_defaults_to_realistic_paint_by_numbers(self):
        serializer = self.serialize()

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["style"], "realistic")
        self.assertEqual(serializer.validated_data["output_mode"], "paint_by_numbers")

    @override_settings(VERTEX_AI_ENABLED=False)
    def test_cartoonish_is_feature_gated(self):
        serializer = self.serialize(style="cartoonish", output_mode="outline_only")

        self.assertFalse(serializer.is_valid())
        self.assertIn("style", serializer.errors)

    @override_settings(VERTEX_AI_ENABLED=True)
    def test_cartoonish_requires_outline_only(self):
        serializer = self.serialize(style="cartoonish")

        self.assertFalse(serializer.is_valid())
        self.assertIn("output_mode", serializer.errors)

    @override_settings(VERTEX_AI_ENABLED=True)
    def test_cartoonish_outline_only_is_accepted(self):
        serializer = self.serialize(style="cartoonish", output_mode="outline_only")

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.extract_params(),
            {"style": "cartoonish", "output_mode": "outline_only"},
        )


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