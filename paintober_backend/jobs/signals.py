"""Signals that dispatch queued jobs to the Cloud Run worker."""

import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Job, JobStatus

logger = logging.getLogger("jobs")


def _execute_cloud_run_job() -> None:
    """Request one execution of the configured Cloud Run Job."""
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account

    project_id = settings.CLOUD_RUN_PROJECT_ID
    job_name = settings.CLOUD_RUN_JOB_NAME
    region = settings.CLOUD_RUN_JOB_REGION
    if not project_id:
        raise RuntimeError("CLOUD_RUN_PROJECT_ID or GCS_PROJECT_ID must be configured")

    credentials_path = getattr(settings, "GCS_CREDENTIALS_PATH", "")
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
    else:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    session = AuthorizedSession(credentials)
    url = (
        "https://run.googleapis.com/v2/projects/"
        f"{project_id}/locations/{region}/jobs/{job_name}:run"
    )
    response = session.post(url, timeout=30)
    response.raise_for_status()

    logger.info(
        "Cloud Run job execution requested | job=%s region=%s operation=%s",
        job_name,
        region,
        response.json().get("name", "unknown"),
    )


@receiver(post_save, sender=Job)
def dispatch_pending_job(
    sender: type[Job],
    instance: Job,
    created: bool,
    update_fields: frozenset[str] | None,
    **kwargs: object,
) -> None:
    """Trigger the worker after a job has been persisted as processable."""
    if not settings.CLOUD_RUN_JOB_ENABLED or instance.status != JobStatus.PENDING:
        return

    # Initial creation happens before the uploaded object is persisted. Only
    # dispatch once the job has an input file and has been queued explicitly.
    if not instance.input_file:
        return
    if update_fields is not None and "status" not in update_fields:
        return

    transaction.on_commit(_dispatch_after_commit)


def _dispatch_after_commit() -> None:
    try:
        _execute_cloud_run_job()
    except Exception:
        # The API request should still succeed; the next scheduler poll or a
        # retry can recover if Cloud Run is temporarily unavailable.
        logger.exception("Could not trigger Cloud Run worker job")