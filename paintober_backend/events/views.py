from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Attendee,
    AttendeeStatus,
    CreditLedgerEntry,
    Event,
    EventStatus,
    LedgerEntryType,
    OrganizerProfile,
)
from .serializers import AttendeeActivitySerializer, AttendeeEntrySerializer, EventCreateSerializer, EventPublicSerializer, EventSerializer
from .services import (
    event_allocated_credits,
    event_available_credits,
    event_consumed_credits,
    organizer_allocated_credits,
    event_reserved_credits,
    organizer_available_credits,
    organizer_total_credits,
)
from jobs.models import Job, JobStatus
from jobs.views import _signed_url
from .throttles import AttendeeEntryThrottle, EventResolutionThrottle

User = get_user_model()
_ATTENDEE_SESSION_KEY = "paintober_attendee_context"


def organizer_profile(request):
    try:
        return request.user.organizer_profile
    except OrganizerProfile.DoesNotExist:
        raise Http404


def public_event_or_404(token):
    try:
        return Event.objects.get(public_token=token)
    except Event.DoesNotExist:
        raise Http404


class OrganizerCreditBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organizer = organizer_profile(request)
        total_credits = organizer_total_credits(organizer)
        allocated_credits = organizer_allocated_credits(organizer)
        return Response({
            "total_credits": total_credits,
            "allocated_credits": allocated_credits,
            "available_credits": max(total_credits - allocated_credits, 0),
        })


class AdminCreditGrantView(APIView):
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request):
        try:
            quantity = int(request.data.get("quantity", 0))
        except (TypeError, ValueError):
            quantity = 0
        if quantity <= 0:
            return Response({"detail": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)
        email = str(request.data.get("email", "")).strip().lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Organizer account not found."}, status=status.HTTP_404_NOT_FOUND)
        organizer, _ = OrganizerProfile.objects.get_or_create(user=user)
        entry = CreditLedgerEntry.objects.create(
            organizer=organizer,
            entry_type=LedgerEntryType.GRANT,
            quantity=quantity,
            note=str(request.data.get("note", "")),
            created_by=request.user,
        )
        return Response({"entry_id": str(entry.id), "available_credits": organizer_available_credits(organizer)}, status=status.HTTP_201_CREATED)


class OrganizerEventListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organizer = organizer_profile(request)
        return Response(EventSerializer(organizer.events.all(), many=True).data)

    @transaction.atomic
    def post(self, request):
        organizer = OrganizerProfile.objects.select_for_update().get(
            pk=organizer_profile(request).pk,
        )
        serializer = EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allocated = serializer.validated_data.pop("allocated_credits")
        if organizer_available_credits(organizer) < allocated:
            return Response({"detail": "Not enough unallocated credits."}, status=status.HTTP_400_BAD_REQUEST)
        event = Event.objects.create(organizer=organizer, **serializer.validated_data)
        CreditLedgerEntry.objects.create(
            organizer=organizer,
            event=event,
            entry_type=LedgerEntryType.ALLOCATION,
            quantity=allocated,
            created_by=request.user,
            note=f"Allocated to event {event.id}",
        )
        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)


class OrganizerEventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, event_id):
        try:
            return Event.objects.get(id=event_id, organizer=organizer_profile(request))
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, event_id):
        event = self.get_object(request, event_id)
        return Response({
            **EventSerializer(event).data,
            "allocated_credits": event_allocated_credits(event),
            "reserved_credits": event_reserved_credits(event),
            "consumed_credits": event_consumed_credits(event),
            "available_credits": event_available_credits(event),
            "attendee_count": event.attendees.count(),
        })

    def patch(self, request, event_id):
        event = self.get_object(request, event_id)
        if request.data.get("status") not in [EventStatus.ACTIVE, EventStatus.DISABLED]:
            return Response({"detail": "Status must be active or disabled."}, status=status.HTTP_400_BAD_REQUEST)
        event.status = request.data["status"]
        event.save(update_fields=["status", "updated_at"])
        return Response(EventSerializer(event).data)


class OrganizerEventKitsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = OrganizerEventDetailView().get_object(request, event_id)
        kits = []
        for job in Job.objects.filter(event=event).order_by("-created_at"):
            kits.append({
                "id": str(job.id),
                "kit_name": job.kit_name,
                "status": job.status,
                "created_at": job.created_at,
                "thumbnail_url": _signed_url(request, job, "color") if job.status == JobStatus.DONE else None,
                "download_url": _signed_url(request, job, "zip") if job.status == JobStatus.DONE else None,
            })
        return Response(kits)


class OrganizerAttendeeActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = OrganizerEventDetailView().get_object(request, event_id)
        attendees = event.attendees.annotate(generation_count=Count("jobs", distinct=True))
        return Response(AttendeeActivitySerializer(attendees, many=True).data)


class OrganizerAttendeeBlockView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, event_id, attendee_id):
        event = OrganizerEventDetailView().get_object(request, event_id)
        try:
            attendee = event.attendees.get(pk=attendee_id)
        except Attendee.DoesNotExist:
            raise Http404
        requested_status = request.data.get("status")
        if requested_status not in [AttendeeStatus.ACTIVE, AttendeeStatus.BLOCKED]:
            return Response({"detail": "Status must be active or blocked."}, status=status.HTTP_400_BAD_REQUEST)
        attendee.status = requested_status
        attendee.save(update_fields=["status", "updated_at"])
        return Response(AttendeeActivitySerializer(attendee).data)


class EventResolveView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [EventResolutionThrottle]

    def get(self, request, event_token):
        event = public_event_or_404(event_token)
        if event.is_expired:
            return Response({"detail": "This event has expired."}, status=status.HTTP_410_GONE)
        if event.status == EventStatus.DISABLED:
            return Response({"detail": "This event is disabled."}, status=status.HTTP_410_GONE)
        if event_available_credits(event) <= 0:
            return Response({"detail": "This event has no credits remaining."}, status=status.HTTP_409_CONFLICT)
        return Response(EventPublicSerializer(event).data)


class EventEnterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AttendeeEntryThrottle]

    def post(self, request):
        serializer = AttendeeEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = public_event_or_404(serializer.validated_data["event_token"])
        if not event.accepts_new_generations:
            return Response({"detail": "This event is not accepting new attendees."}, status=status.HTTP_410_GONE)
        if event_available_credits(event) <= 0:
            return Response({"detail": "This event has no credits remaining."}, status=status.HTTP_409_CONFLICT)
        if event.otp_required:
            return Response(
                {"detail": "Phone verification is required for this event but is not enabled yet."},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        attendee, _ = Attendee.objects.get_or_create(
            event=event,
            phone_number=serializer.validated_data["phone_number"],
        )
        if attendee.status == AttendeeStatus.BLOCKED:
            return Response({"detail": "This attendee is blocked for the event."}, status=status.HTTP_403_FORBIDDEN)
        request.session[_ATTENDEE_SESSION_KEY] = {
            "event_id": str(event.id),
            "attendee_id": attendee.id,
        }
        request.session.save()
        return Response({
            "attendee_id": attendee.id,
            "event": EventPublicSerializer(event).data,
        })
