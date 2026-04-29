import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core import signing
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema

from .models import Job, JobStatus
from .serializers import JobCreateResponseSerializer, JobCreateSerializer, JobListSerializer, JobStatusSerializer
from .throttles import JobCreationThrottle

logger = logging.getLogger("jobs")

_DOWNLOAD_SALT = "paintober-download"
_DOWNLOAD_MAX_AGE = 3600  # seconds (1 hour)

_FILE_FIELD_MAP = {
    "outline": "output_outline",
    "color": "output_color",
    "palette": "output_palette",
    "zip": "output_zip",
}


def _signed_url(request: Request, job: Job, file_key: str) -> str:
    token = signing.dumps(
        {"job_id": str(job.id), "file": file_key},
        salt=_DOWNLOAD_SALT,
    )
    return request.build_absolute_uri(f"/api/jobs/{job.id}/download/{file_key}/?token={token}")


def _get_owner_filter(request: Request) -> dict:
    if request.user and request.user.is_authenticated:
        return {"user": request.user}
    key = request.session.session_key
    if key:
        return {"session_key": key}
    return {"pk": None}  # no match — no jobs for this request


class JobCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]
    throttle_classes = [JobCreationThrottle]
    serializer_class = JobCreateSerializer

    MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

    @extend_schema(responses={201: JobCreateResponseSerializer})
    def post(self, request: Request) -> Response:
        # Ensure session exists for anonymous users so we can scope jobs
        if not request.session.session_key:
            request.session.create()

        serializer = JobCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image_file = serializer.validated_data["image"]

        # File size guard
        if image_file.size > self.MAX_UPLOAD_BYTES:
            return Response(
                {"detail": "Image exceeds the 50 MB limit."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Free-tier guard
        free_limit = getattr(settings, "FREE_JOBS_PER_DAY", 3)
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        owner_filter = _get_owner_filter(request)
        jobs_today = Job.objects.filter(**owner_filter, created_at__gte=today_start).count()

        has_credits = (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.credits > 0
        )
        if jobs_today >= free_limit and not has_credits:
            return Response(
                {
                    "detail": (
                        f"Free limit of {free_limit} jobs/day reached. "
                        "Purchase credits to continue."
                    )
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        # Save upload
        job = Job(parameters=serializer.extract_params())
        if request.user.is_authenticated:
            job.user = request.user
        else:
            job.session_key = request.session.session_key
        job.save()

        upload_dir = Path(settings.MEDIA_ROOT) / "uploads" / str(job.id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(image_file.name).suffix.lower() or ".png"
        dest = upload_dir / f"original{suffix}"
        with open(dest, "wb") as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # Normalise to PNG
        from pipeline.processor import normalise_upload, SUPPORTED_FORMATS
        if suffix not in SUPPORTED_FORMATS:
            job.delete()
            return Response(
                {"detail": f"Unsupported format '{suffix}'. Accepted: jpg, jpeg, png, webp."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        png_dest = upload_dir / "original.png"
        try:
            normalise_upload(dest, png_dest)
        except Exception as exc:
            job.delete()
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if dest != png_dest:
            dest.unlink(missing_ok=True)

        job.input_file = str(png_dest.relative_to(settings.MEDIA_ROOT))
        job.status = JobStatus.PENDING
        job.save(update_fields=["input_file", "status", "updated_at"])

        logger.info("Job created | job_id=%s user=%s", job.id, job.user_id or job.session_key)

        return Response(
            {"job_id": str(job.id), "status": job.status},
            status=status.HTTP_201_CREATED,
        )


class JobDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = JobStatusSerializer

    @extend_schema(operation_id="job_retrieve")
    def get(self, request: Request, job_id: str) -> Response:
        owner_filter = _get_owner_filter(request)
        if "pk" in owner_filter:
            # No session and no authenticated user — cannot own any job
            raise Http404
        try:
            job = Job.objects.get(pk=job_id, **owner_filter)
        except Job.DoesNotExist:
            raise Http404
        serializer = JobStatusSerializer(job, context={"request": request})
        return Response(serializer.data)


class JobListView(APIView):
    permission_classes = [AllowAny]
    serializer_class = JobListSerializer

    @extend_schema(operation_id="job_list")
    def get(self, request: Request) -> Response:
        owner_filter = _get_owner_filter(request)
        jobs = Job.objects.filter(**owner_filter)
        serializer = JobListSerializer(jobs, many=True)
        return Response(serializer.data)


class JobDownloadView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="file_key",
                location=OpenApiParameter.PATH,
                enum=["outline", "color", "palette", "zip"],
                description="Output file to download.",
            ),
            OpenApiParameter(
                name="token",
                location=OpenApiParameter.QUERY,
                type=str,
                required=True,
                description="Signed download token from the job detail response. Expires after 1 hour.",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="PNG image or ZIP archive.",
            ),
            403: OpenApiResponse(description="Token expired or invalid."),
            404: OpenApiResponse(description="Job not done or file not found."),
        },
    )
    def get(self, request: Request, job_id: str, file_key: str) -> Response:
        token = request.query_params.get("token", "")
        try:
            payload = signing.loads(token, salt=_DOWNLOAD_SALT, max_age=_DOWNLOAD_MAX_AGE)
        except signing.SignatureExpired:
            return Response({"detail": "Download link expired."}, status=status.HTTP_403_FORBIDDEN)
        except signing.BadSignature:
            return Response({"detail": "Invalid download token."}, status=status.HTTP_403_FORBIDDEN)

        if payload.get("job_id") != str(job_id) or payload.get("file") != file_key:
            return Response({"detail": "Token mismatch."}, status=status.HTTP_403_FORBIDDEN)

        field = _FILE_FIELD_MAP.get(file_key)
        if field is None:
            raise Http404

        try:
            job = Job.objects.get(pk=job_id, status=JobStatus.DONE)
        except Job.DoesNotExist:
            raise Http404

        relative_path = getattr(job, field, "")
        if not relative_path:
            raise Http404

        abs_path = Path(settings.MEDIA_ROOT) / relative_path
        if not abs_path.exists():
            raise Http404

        content_type, _ = mimetypes.guess_type(str(abs_path))
        response = FileResponse(
            open(abs_path, "rb"),
            content_type=content_type or "application/octet-stream",
        )
        response["Content-Disposition"] = f'attachment; filename="{abs_path.name}"'
        return response
