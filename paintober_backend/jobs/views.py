import logging
import mimetypes
import tempfile
from pathlib import Path

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema

from events.models import Attendee, Event, OrganizerProfile
from events.services import organizer_available_credits, reserve_event_credit, release_credit_reservation

from .models import Job, JobStatus
from .serializers import JobCreateResponseSerializer, JobCreateSerializer, JobListSerializer, JobStatusSerializer
from .storage import get_job_storage
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


def _get_attendee_context(request: Request):
    context = request.session.get("paintober_attendee_context")
    if not context:
        return None
    try:
        attendee_id = int(context["attendee_id"])
        event_id = context["event_id"]
        return Attendee.objects.select_related("event").get(pk=attendee_id, event_id=event_id)
    except (KeyError, TypeError, ValueError, Attendee.DoesNotExist):
        return None


def _authorized_jobs(request: Request, allowsuperuser=False):
    attendee = _get_attendee_context(request)
    if attendee is not None:
        return Job.objects.filter(event=attendee.event, attendee=attendee)
    if request.user and request.user.is_authenticated:
        if request.user.is_super_user and allowsuperuser:
            return Job.objects.all()
        return Job.objects.filter(
            Q(user=request.user) | Q(event__organizer__user=request.user)
        ).distinct()
    key = request.session.session_key
    if key:
        return Job.objects.filter(session_key=key, event__isnull=True)
    return Job.objects.none()


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

        attendee = _get_attendee_context(request)
        requested_event_id = serializer.validated_data.get("event_id")
        if attendee is not None and requested_event_id is not None:
            return Response(
                {"detail": "The attendee event context cannot be changed here."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        organizer_event = None
        if requested_event_id is not None:
            if not request.user.is_authenticated:
                return Response({"detail": "Sign in to create an event kit."}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                organizer_event = Event.objects.get(
                    id=requested_event_id,
                    organizer__user=request.user,
                )
            except Event.DoesNotExist:
                return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
            if not organizer_event.accepts_new_generations:
                return Response({"detail": "This event is not accepting new generations."}, status=status.HTTP_409_CONFLICT)

        # Free-tier guard applies only to the retained anonymous flow.
        free_limit = getattr(settings, "FREE_JOBS_PER_DAY", 3)
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        owner_filter = _get_owner_filter(request)
        jobs_today = Job.objects.filter(**owner_filter, created_at__gte=today_start).count()

        has_credits = (
            request.user.is_authenticated
            and hasattr(request.user, "organizer_profile")
            and organizer_available_credits(request.user.organizer_profile) > 0
        )
        if attendee is None and jobs_today >= free_limit and not has_credits:
            return Response(
                {
                    "detail": (
                        f"Free limit of {free_limit} jobs/day reached. "
                        "Purchase credits to continue."
                    )
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        from pipeline.processor import normalise_upload, SUPPORTED_FORMATS

        suffix = Path(image_file.name).suffix.lower() or ".png"
        if suffix not in SUPPORTED_FORMATS:
            return Response(
                {"detail": f"Unsupported format '{suffix}'. Accepted: jpg, jpeg, png, webp."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            storage = get_job_storage()
        except Exception:
            logger.exception("Could not initialize job storage")
            return Response(
                {"detail": "Image storage is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Create the job and reserve an event credit before committing it to the queue.
        job = Job(
            parameters=serializer.extract_params(),
            kit_name=serializer.validated_data.get("kit_name", "").strip() or None,
        )
        if attendee is not None:
            job.event = attendee.event
            job.attendee = attendee
        elif organizer_event is not None:
            job.event = organizer_event
            job.user = request.user
        elif request.user.is_authenticated:
            job.user = request.user
        else:
            job.session_key = request.session.session_key
        try:
            with transaction.atomic():
                job.save()
                if attendee is not None or organizer_event is not None:
                    reservation = reserve_event_credit(
                        attendee.event_id if attendee is not None else organizer_event.id,
                        attendee.id if attendee is not None else None,
                        job.id,
                    )
                else:
                    reservation = None

                if settings.GCS_ENABLED:
                    input_key = f"{settings.GCS_OBJECT_PREFIX}/{job.id}/input/original.png"
                else:
                    input_key = f"uploads/{job.id}/original.png"
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir_path = Path(temp_dir)
                    source = temp_dir_path / f"original{suffix}"
                    png_dest = temp_dir_path / "original.png"
                    with source.open("wb") as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                    normalise_upload(source, png_dest)
                    storage.save_upload(input_key, png_dest, "image/png")
                job.input_file = input_key
                job.status = JobStatus.PENDING
                job.save(update_fields=["input_file", "status", "updated_at"])
        except Exception as exc:
            if "input_key" in locals():
                storage.delete_upload(input_key)
            if isinstance(exc, ValueError):
                return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

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
        # if "pk" in owner_filter:
        #     # No session and no authenticated user — cannot own any job
        #     raise Http404
        try:
            job = _authorized_jobs(request, allowsuperuser=True).get(pk=job_id)
        except Job.DoesNotExist:
            raise Http404
        serializer = JobStatusSerializer(job, context={"request": request})
        return Response(serializer.data)


class JobRenameView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, job_id: str) -> Response:
        try:
            job = _authorized_jobs(request).get(pk=job_id)
        except Job.DoesNotExist:
            raise Http404
        if not (job.user_id == request.user.id or job.event_id and job.event.organizer.user_id == request.user.id):
            raise Http404
        kit_name = request.data.get("kit_name", "")
        if kit_name is None:
            kit_name = ""
        kit_name = str(kit_name).strip()
        if len(kit_name) > 200:
            return Response({"detail": "Kit name must be 200 characters or fewer."}, status=status.HTTP_400_BAD_REQUEST)
        job.kit_name = kit_name or None
        job.save(update_fields=["kit_name", "updated_at"])
        return Response(JobStatusSerializer(job, context={"request": request}).data)


class JobListView(APIView):
    permission_classes = [AllowAny]
    serializer_class = JobListSerializer

    @extend_schema(operation_id="job_list")
    def get(self, request: Request) -> Response:
        jobs = _authorized_jobs(request)
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
            job = _authorized_jobs(request).get(pk=job_id, status=JobStatus.DONE)
        except Job.DoesNotExist:
            raise Http404

        relative_path = getattr(job, field, "")
        if not relative_path:
            raise Http404

        storage = get_job_storage()
        if not storage.result_exists(relative_path):
            raise Http404

        if storage.is_remote:
            return HttpResponseRedirect(
                storage.signed_result_url(
                    relative_path, settings.GCS_SIGNED_URL_EXPIRY_SECONDS
                )
            )

        abs_path = Path(settings.MEDIA_ROOT) / relative_path
        content_type, _ = mimetypes.guess_type(relative_path)
        response = FileResponse(
            open(abs_path, "rb"),
            content_type=content_type or "application/octet-stream",
        )
        response["Content-Disposition"] = f'attachment; filename="{abs_path.name}"'
        return response
