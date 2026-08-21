from django.db import transaction
from django.db.models import Sum

from .models import (
    Attendee,
    AttendeeStatus,
    CreditLedgerEntry,
    CreditReservation,
    CreditReservationStatus,
    Event,
    LedgerEntryType,
)


def organizer_available_credits(organizer):
    grants = CreditLedgerEntry.objects.filter(
        organizer=organizer,
        event__isnull=True,
        entry_type__in=[LedgerEntryType.GRANT, LedgerEntryType.ADJUSTMENT],
    ).aggregate(total=Sum("quantity"))["total"] or 0
    allocated = CreditLedgerEntry.objects.filter(
        organizer=organizer,
        entry_type=LedgerEntryType.ALLOCATION,
    ).aggregate(total=Sum("quantity"))["total"] or 0
    return max(grants - allocated, 0)


def event_allocated_credits(event):
    return CreditLedgerEntry.objects.filter(
        event=event,
        entry_type=LedgerEntryType.ALLOCATION,
    ).aggregate(total=Sum("quantity"))["total"] or 0


def event_reserved_credits(event):
    return CreditReservation.objects.filter(
        event=event,
        status=CreditReservationStatus.RESERVED,
    ).aggregate(total=Sum("quantity"))["total"] or 0


def event_consumed_credits(event):
    return CreditReservation.objects.filter(
        event=event,
        status=CreditReservationStatus.CONSUMED,
    ).aggregate(total=Sum("quantity"))["total"] or 0


def event_available_credits(event):
    return max(
        event_allocated_credits(event)
        - event_reserved_credits(event)
        - event_consumed_credits(event),
        0,
    )


def attendee_completed_or_reserved_kits(attendee):
    return CreditReservation.objects.filter(
        attendee=attendee,
        status__in=[CreditReservationStatus.RESERVED, CreditReservationStatus.CONSUMED],
    ).aggregate(total=Sum("quantity"))["total"] or 0


@transaction.atomic
def reserve_event_credit(event_id, attendee_id, job_id):
    event = Event.objects.select_for_update().select_related("organizer").get(pk=event_id)
    attendee = None
    if attendee_id is not None:
        attendee = Attendee.objects.select_for_update().get(pk=attendee_id, event=event)

    if not event.accepts_new_generations:
        raise ValueError("This event is not accepting new generations.")
    if attendee is not None:
        if attendee.status != AttendeeStatus.ACTIVE:
            raise ValueError("This attendee is blocked for the event.")
        if attendee_completed_or_reserved_kits(attendee) >= event.max_kits_per_attendee:
            raise ValueError("This attendee has reached the event kit limit.")
    if event_available_credits(event) < 1:
        raise ValueError("This event has no credits remaining.")

    reservation = CreditReservation.objects.create(
        organizer=event.organizer,
        event=event,
        attendee=attendee,
        job_id=job_id,
        quantity=1,
    )
    CreditLedgerEntry.objects.create(
        organizer=event.organizer,
        event=event,
        entry_type=LedgerEntryType.RESERVATION,
        quantity=-reservation.quantity,
        reference=reservation.id,
        note=f"Reserved for job {job_id}",
    )
    return reservation


@transaction.atomic
def finalize_credit_reservation(job_id):
    reservation = CreditReservation.objects.select_for_update().select_related("event", "organizer").get(job_id=job_id)
    if reservation.status != CreditReservationStatus.RESERVED:
        return reservation
    reservation.status = CreditReservationStatus.CONSUMED
    reservation.save(update_fields=["status", "updated_at"])
    CreditLedgerEntry.objects.create(
        organizer=reservation.organizer,
        event=reservation.event,
        entry_type=LedgerEntryType.CONSUMPTION,
        quantity=0,
        reference=reservation.id,
        note=f"Finalized for job {job_id}",
    )
    return reservation


@transaction.atomic
def release_credit_reservation(job_id, note=""):
    reservation = CreditReservation.objects.select_for_update().select_related("event", "organizer").get(job_id=job_id)
    if reservation.status != CreditReservationStatus.RESERVED:
        return reservation
    reservation.status = CreditReservationStatus.RELEASED
    reservation.save(update_fields=["status", "updated_at"])
    CreditLedgerEntry.objects.create(
        organizer=reservation.organizer,
        event=reservation.event,
        entry_type=LedgerEntryType.RELEASE,
        quantity=reservation.quantity,
        reference=reservation.id,
        note=note or f"Released for job {job_id}",
    )
    return reservation
