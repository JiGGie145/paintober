import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class JobStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    DONE = "done", "Done"
    FAILED = "failed", "Failed"


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Owner — one of these will be set; both nullable to support anonymous users
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs",
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)

    status = models.CharField(
        max_length=12,
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
        db_index=True,
    )
    retry_count = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    # Pipeline parameters supplied at submission time
    parameters = models.JSONField(default=dict)

    # File paths stored relative to MEDIA_ROOT
    input_file = models.CharField(max_length=512, blank=True, default="")
    output_outline = models.CharField(max_length=512, blank=True, default="")
    output_color = models.CharField(max_length=512, blank=True, default="")
    output_palette = models.CharField(max_length=512, blank=True, default="")
    output_zip = models.CharField(max_length=512, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        owner = self.user_id or self.session_key or "anonymous"
        return f"Job {self.id} [{self.status}] owner={owner}"
