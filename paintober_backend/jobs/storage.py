"""Storage operations for job inputs and generated assets."""

from datetime import timedelta
from pathlib import Path

from django.conf import settings


def _safe_key(key: str) -> str:
    """Reject object keys that could escape the local storage root."""
    path = Path(key)
    if not key or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Invalid storage key: {key!r}")
    return key


class LocalJobStorage:
    is_remote = False

    def _path(self, key: str) -> Path:
        return Path(settings.MEDIA_ROOT) / _safe_key(key)

    def save_upload(self, key: str, source: Path, content_type: str) -> str:
        return self._save_file(key, source)

    def save_result(self, key: str, source: Path, content_type: str) -> str:
        return self._save_file(key, source)

    def _save_file(self, key: str, source: Path) -> str:
        destination = self._path(key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        return key

    def download_upload(self, key: str, destination: Path) -> None:
        self._download_file(key, destination)

    def _download_file(self, key: str, destination: Path) -> None:
        source = self._path(key)
        if not source.exists():
            raise FileNotFoundError(key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    def delete_upload(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)

    def upload_exists(self, key: str) -> bool:
        return self._path(key).exists()

    def result_exists(self, key: str) -> bool:
        return self._path(key).exists()

    def signed_result_url(self, key: str, expiration_seconds: int) -> str:
        return str(self._path(key))


class GCSJobStorage:
    is_remote = True

    def __init__(self) -> None:
        from google.cloud import storage
        from google.oauth2 import service_account

        credentials_path = getattr(settings, "GCS_CREDENTIALS_PATH", "")
        credentials = (
            service_account.Credentials.from_service_account_file(credentials_path)
            if credentials_path 
            else None
        )

        client_kwargs = {
            "project": getattr(settings, "GCS_PROJECT_ID", None) or None,
        }
        if credentials is not None:
            client_kwargs["credentials"] = credentials
        self.client = storage.Client(**client_kwargs)
        self.upload_bucket = self.client.bucket(settings.GCS_UPLOAD_BUCKET_NAME)
        self.results_bucket = self.client.bucket(settings.GCS_RESULTS_BUCKET_NAME)

    def _blob(self, bucket, key: str):
        return bucket.blob(_safe_key(key))

    def save_upload(self, key: str, source: Path, content_type: str) -> str:
        self._blob(self.upload_bucket, key).upload_from_filename(
            str(source), content_type=content_type
        )
        return key

    def download_upload(self, key: str, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._blob(self.upload_bucket, key).download_to_filename(str(destination))

    def delete_upload(self, key: str) -> None:
        self._blob(self.upload_bucket, key).delete(ignore_not_found=True)

    def upload_exists(self, key: str) -> bool:
        return self._blob(self.upload_bucket, key).exists()

    def save_result(self, key: str, source: Path, content_type: str) -> str:
        self._blob(self.results_bucket, key).upload_from_filename(
            str(source), content_type=content_type
        )
        return key

    def result_exists(self, key: str) -> bool:
        return self._blob(self.results_bucket, key).exists()

    def signed_result_url(self, key: str, expiration_seconds: int) -> str:
        return self._blob(self.results_bucket, key).generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration_seconds),
            method="GET",
        )


def get_job_storage() -> LocalJobStorage | GCSJobStorage:
    if settings.GCS_ENABLED:
        return GCSJobStorage()
    return LocalJobStorage()