import logging
from pathlib import Path

from django.conf import settings
from django.db import transaction

from jobs.models import Job, JobStatus
from pipeline.processor import run_pipeline

logger = logging.getLogger("jobs")


def _media(relative_path: str) -> str:
    """Return absolute path string for a MEDIA_ROOT-relative path."""
    return str(Path(settings.MEDIA_ROOT) / relative_path)


def _relative(absolute_path: str) -> str:
    """Return MEDIA_ROOT-relative path string from an absolute path."""
    return str(Path(absolute_path).relative_to(settings.MEDIA_ROOT))


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
        image_abs = _media(job.input_file)
        output_dir = Path(settings.MEDIA_ROOT) / "outputs" / job_id

        result = run_pipeline(image_abs, output_dir, job.parameters)

        with transaction.atomic():
            job.refresh_from_db()
            job.status = JobStatus.DONE
            job.output_outline = _relative(result["output_outline"])
            job.output_color = _relative(result["output_color"])
            job.output_palette = _relative(result["output_palette"])
            job.output_zip = _relative(result["output_zip"])
            job.save(update_fields=[
                "status", "output_outline", "output_color",
                "output_palette", "output_zip", "updated_at",
            ])

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
