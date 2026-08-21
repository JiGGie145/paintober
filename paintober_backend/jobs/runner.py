import logging
import tempfile
from pathlib import Path

from django.conf import settings
from django.db import transaction

from events.services import finalize_credit_reservation, release_credit_reservation

from jobs.models import Job, JobStatus
from jobs.storage import get_job_storage
from pipeline.processor import run_pipeline

logger = logging.getLogger("jobs")


def poll_and_process() -> None:
    """Claim one pending job and process it.

    Uses SELECT FOR UPDATE SKIP LOCKED so concurrent scheduler processes
    (if ever added) cannot double-claim the same job.
    Note: SQLite does not support SKIP LOCKED — safe here because we run a
    single scheduler process. Upgrading to PostgreSQL enables full support.
    """
    with transaction.atomic():
        try:
            job = (
                Job.objects.select_for_update(skip_locked=True)
                .filter(status=JobStatus.PENDING)
                .order_by("created_at")
                .first()
            )
        except Exception:
            # SQLite raises OperationalError for skip_locked; fall back.
            job = (
                Job.objects.select_for_update()
                .filter(status=JobStatus.PENDING)
                .order_by("created_at")
                .first()
            )

        if job is None:
            return

        job.status = JobStatus.PROCESSING
        job.save(update_fields=["status", "updated_at"])
        job_id = str(job.id)

    logger.info("Job claimed | job_id=%s retry=%d", job_id, job.retry_count)

    try:
        storage = get_job_storage()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            image_path = temp_root / "input.png"
            output_dir = temp_root / "outputs"
            storage.download_upload(job.input_file, image_path)
            result = run_pipeline(str(image_path), output_dir, job.parameters)

            output_keys = {
                "output_outline": f"{settings.GCS_OBJECT_PREFIX}/{job_id}/outputs/outline.png" if settings.GCS_ENABLED else f"outputs/{job_id}/outline.png",
                "output_color": f"{settings.GCS_OBJECT_PREFIX}/{job_id}/outputs/quantized_color.png" if settings.GCS_ENABLED else f"outputs/{job_id}/quantized_color.png",
                "output_palette": f"{settings.GCS_OBJECT_PREFIX}/{job_id}/outputs/palette.png" if settings.GCS_ENABLED else f"outputs/{job_id}/palette.png",
                "output_zip": f"{settings.GCS_OBJECT_PREFIX}/{job_id}/outputs/results.zip" if settings.GCS_ENABLED else f"outputs/{job_id}/results.zip",
            }
            content_types = {
                "output_outline": "image/png",
                "output_color": "image/png",
                "output_palette": "image/png",
                "output_zip": "application/zip",
            }
            stored_outputs = {
                field: storage.save_result(
                    output_keys[field], Path(result[field]), content_types[field]
                )
                for field in output_keys
            }

        with transaction.atomic():
            job.refresh_from_db()
            job.status = JobStatus.DONE
            job.output_outline = stored_outputs["output_outline"]
            job.output_color = stored_outputs["output_color"]
            job.output_palette = stored_outputs["output_palette"]
            job.output_zip = stored_outputs["output_zip"]
            job.save(update_fields=[
                "status", "output_outline", "output_color",
                "output_palette", "output_zip", "updated_at",
            ])
            if job.event_id:
                finalize_credit_reservation(job.id)

        logger.info("Job done | job_id=%s", job_id)

    except Exception as exc:
        logger.error("Job failed | job_id=%s retry=%d error=%s", job_id, job.retry_count, exc, exc_info=True)

        with transaction.atomic():
            job.refresh_from_db()
            job.retry_count += 1
            if job.retry_count < settings.JOB_MAX_RETRIES:
                job.status = JobStatus.PENDING
                logger.info(
                    "Job queued for retry | job_id=%s retry=%d/%d",
                    job_id, job.retry_count, settings.JOB_MAX_RETRIES,
                )
            else:
                job.status = JobStatus.FAILED
                job.error_message = str(exc)
                logger.error(
                    "Job permanently failed | job_id=%s retries_exhausted=%d",
                    job_id, job.retry_count,
                )
            job.save(update_fields=["status", "retry_count", "error_message", "updated_at"])
            if job.status == JobStatus.FAILED and job.event_id:
                release_credit_reservation(job.id, note=str(exc))
