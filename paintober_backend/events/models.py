import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_event_token():
    return secrets.token_urlsafe(8)


class OrganizerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizer_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_username()


class EventStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    DISABLED = "disabled", "Disabled"


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(
        OrganizerProfile,
        on_delete=models.CASCADE,
        related_name="events",
    )
    name = models.CharField(max_length=200)
    event_date = models.DateField()
    public_token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_event_token,
        editable=False,
    )
    status = models.CharField(
        max_length=12,
        choices=EventStatus.choices,
        default=EventStatus.ACTIVE,
        db_index=True,
    )
    otp_required = models.BooleanField(default=False)
    max_kits_per_attendee = models.PositiveIntegerField(default=1)
    branding = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]

    @property
    def is_expired(self):
        return self.event_date < timezone.localdate()

    @property
    def accepts_new_generations(self):
        return self.status == EventStatus.ACTIVE and not self.is_expired

    def __str__(self):
        return self.name


class AttendeeStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    BLOCKED = "blocked", "Blocked"


class Attendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees")
    phone_number = models.CharField(max_length=32)
    status = models.CharField(
        max_length=12,
        choices=AttendeeStatus.choices,
        default=AttendeeStatus.ACTIVE,
    )
    otp_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "phone_number"],
                name="unique_attendee_phone_per_event",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event.name}: {self.phone_number}"


class LedgerEntryType(models.TextChoices):
    GRANT = "grant", "Grant"
    ALLOCATION = "allocation", "Allocation"
    ADJUSTMENT = "adjustment", "Adjustment"
    RESERVATION = "reservation", "Reservation"
    CONSUMPTION = "consumption", "Consumption"
    RELEASE = "release", "Release"


class CreditLedgerEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(
        OrganizerProfile,
        on_delete=models.PROTECT,
        related_name="credit_entries",
    )
    event = models.ForeignKey(
        Event,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="credit_entries",
    )
    entry_type = models.CharField(max_length=16, choices=LedgerEntryType.choices)
    quantity = models.IntegerField()
    reference = models.UUIDField(default=uuid.uuid4, editable=False)
    note = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_credit_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organizer", "entry_type"]),
            models.Index(fields=["event", "entry_type"]),
        ]


class CreditReservationStatus(models.TextChoices):
    RESERVED = "reserved", "Reserved"
    CONSUMED = "consumed", "Consumed"
    RELEASED = "released", "Released"


class CreditReservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(OrganizerProfile, on_delete=models.PROTECT, related_name="reservations")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="reservations")
    attendee = models.ForeignKey(Attendee, null=True, blank=True, on_delete=models.PROTECT, related_name="reservations")
    job_id = models.UUIDField(null=True, blank=True, unique=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=12,
        choices=CreditReservationStatus.choices,
        default=CreditReservationStatus.RESERVED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["event", "status"]),
            models.Index(fields=["attendee", "status"]),
        ]
