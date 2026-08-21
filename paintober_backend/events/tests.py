from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.test import override_settings
from rest_framework.test import APIClient

from jobs.models import Job, JobStatus

from .models import (
    Attendee,
    AttendeeStatus,
    CreditLedgerEntry,
    CreditReservation,
    CreditReservationStatus,
    Event,
    EventStatus,
    LedgerEntryType,
    OrganizerProfile,
)
from .services import finalize_credit_reservation, release_credit_reservation, reserve_event_credit

User = get_user_model()


class EventAccessApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="organizer@example.com",
            email="organizer@example.com",
            password="strong-password-123",
        )
        self.organizer = OrganizerProfile.objects.create(user=self.user)
        CreditLedgerEntry.objects.create(
            organizer=self.organizer,
            entry_type=LedgerEntryType.GRANT,
            quantity=5,
        )
        self.event = Event.objects.create(
            organizer=self.organizer,
            name="Tsholo's Sip & Paint",
            event_date=date.today() + timedelta(days=30),
        )
        CreditLedgerEntry.objects.create(
            organizer=self.organizer,
            event=self.event,
            entry_type=LedgerEntryType.ALLOCATION,
            quantity=2,
        )

    def test_registration_and_session_me(self):
        response = self.client.post(
            "/api/auth/register/",
            {"email": "new@example.com", "password": "strong-password-123"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)

    def test_organizer_can_list_events_and_balance(self):
        self.client.force_login(self.user)
        balance = self.client.get("/api/events/credits/")
        events = self.client.get("/api/events/mine/")
        self.assertEqual(balance.data["available_credits"], 3)
        self.assertEqual(events.status_code, 200)
        self.assertEqual(events.data[0]["name"], self.event.name)

    def test_event_can_be_resolved_and_attendee_can_enter(self):
        token = self.event.public_token
        resolved = self.client.get(f"/api/events/resolve/{token}/")
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.data["name"], self.event.name)

        entered = self.client.post(
            "/api/events/enter/",
            {"event_token": token, "phone_number": "(071) 234-5678"},
            format="json",
        )
        self.assertEqual(entered.status_code, 200)
        self.assertEqual(entered.data["event"]["token"], token)
        self.assertEqual(Attendee.objects.count(), 1)
        self.assertEqual(Attendee.objects.get().phone_number, "+0712345678")
        self.assertIn("paintober_attendee_context", self.client.session)

    def test_blocked_attendee_cannot_enter(self):
        attendee = Attendee.objects.create(event=self.event, phone_number="+27123456789", status="blocked")
        response = self.client.post(
            "/api/events/enter/",
            {"event_token": self.event.public_token, "phone_number": attendee.phone_number},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_disabled_event_cannot_be_resolved(self):
        self.event.status = EventStatus.DISABLED
        self.event.save(update_fields=["status"])
        response = self.client.get(f"/api/events/resolve/{self.event.public_token}/")
        self.assertEqual(response.status_code, 410)

    def test_reservation_is_available_once_and_finalization_is_idempotent(self):
        job_id = "2b7f4d1b-45a6-4f0a-8a4f-2ac1d9e0f001"
        attendee = Attendee.objects.create(event=self.event, phone_number="+27123456789")
        reservation = reserve_event_credit(self.event.id, attendee.id, job_id)

        self.assertEqual(reservation.status, CreditReservationStatus.RESERVED)
        self.assertEqual(CreditReservation.objects.count(), 1)
        self.assertEqual(
            CreditLedgerEntry.objects.filter(entry_type=LedgerEntryType.RESERVATION).count(),
            1,
        )
        second_attendee = Attendee.objects.create(event=self.event, phone_number="+27111111111")
        reserve_event_credit(
            self.event.id,
            second_attendee.id,
            "2b7f4d1b-45a6-4f0a-8a4f-2ac1d9e0f002",
        )
        third_attendee = Attendee.objects.create(event=self.event, phone_number="+27222222222")
        with self.assertRaisesMessage(ValueError, "no credits remaining"):
            reserve_event_credit(
                self.event.id,
                third_attendee.id,
                "2b7f4d1b-45a6-4f0a-8a4f-2ac1d9e0f003",
            )

        finalize_credit_reservation(job_id)
        finalize_credit_reservation(job_id)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, CreditReservationStatus.CONSUMED)
        self.assertEqual(
            CreditLedgerEntry.objects.filter(entry_type=LedgerEntryType.CONSUMPTION).count(),
            1,
        )

    def test_failed_reservation_is_released_and_can_be_retried(self):
        attendee = Attendee.objects.create(event=self.event, phone_number="+27123456789")
        first_job_id = "2b7f4d1b-45a6-4f0a-8a4f-2ac1d9e0f003"
        reserve_event_credit(self.event.id, attendee.id, first_job_id)
        release_credit_reservation(first_job_id, note="pipeline failed")

        self.assertEqual(
            CreditReservation.objects.get(job_id=first_job_id).status,
            CreditReservationStatus.RELEASED,
        )
        second_job_id = "2b7f4d1b-45a6-4f0a-8a4f-2ac1d9e0f004"
        retry = reserve_event_credit(self.event.id, attendee.id, second_job_id)
        self.assertEqual(retry.status, CreditReservationStatus.RESERVED)

    def test_job_detail_is_scoped_to_event_attendee_context(self):
        attendee = Attendee.objects.create(event=self.event, phone_number="+27123456789")
        job = Job.objects.create(
            event=self.event,
            attendee=attendee,
            status=JobStatus.PROCESSING,
            parameters={},
        )
        self.client.post(
            "/api/events/enter/",
            {"event_token": self.event.public_token, "phone_number": attendee.phone_number},
            format="json",
        )
        self.assertEqual(self.client.get(f"/api/jobs/{job.id}/").status_code, 200)

        other_client = APIClient()
        other_client.post(
            "/api/events/enter/",
            {"event_token": self.event.public_token, "phone_number": "+27987654321"},
            format="json",
        )
        self.assertEqual(other_client.get(f"/api/jobs/{job.id}/").status_code, 404)

    def test_organizer_event_kits_include_all_statuses_and_thumbnail_for_done(self):
        self.client.force_login(self.user)
        done_job = Job.objects.create(
            user=self.user,
            event=self.event,
            kit_name="Garden kit",
            status=JobStatus.DONE,
            output_color="outputs/done/quantized_color.png",
        )
        Job.objects.create(
            user=self.user,
            event=self.event,
            status=JobStatus.PROCESSING,
        )

        response = self.client.get(f"/api/events/mine/{self.event.id}/kits/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        done_data = next(item for item in response.data if item["id"] == str(done_job.id))
        self.assertEqual(done_data["kit_name"], "Garden kit")
        self.assertIsNotNone(done_data["thumbnail_url"])
        processing_data = next(item for item in response.data if item["status"] == JobStatus.PROCESSING)
        self.assertIsNone(processing_data["thumbnail_url"])

    def test_organizer_can_rename_owned_event_kit_but_not_other_organizer_kit(self):
        self.client.force_login(self.user)
        job = Job.objects.create(user=self.user, event=self.event, status=JobStatus.PENDING)

        renamed = self.client.patch(
            f"/api/jobs/{job.id}/rename/",
            {"kit_name": "Renamed kit"},
            format="json",
        )
        self.assertEqual(renamed.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.kit_name, "Renamed kit")

        other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="strong-password-123",
        )
        OrganizerProfile.objects.create(user=other_user)
        self.client.force_login(other_user)
        self.assertEqual(
            self.client.patch(
                f"/api/jobs/{job.id}/rename/",
                {"kit_name": "No access"},
                format="json",
            ).status_code,
            404,
        )

    def test_organizer_event_reservation_does_not_require_attendee(self):
        reservation = reserve_event_credit(
            self.event.id,
            None,
            "2b7f4d1b-45a6-4f0a-8a4f-2ac1d9e0f005",
        )

        self.assertIsNone(reservation.attendee_id)
        self.assertEqual(reservation.status, CreditReservationStatus.RESERVED)

    def test_organizer_attendee_activity_masks_phone_and_counts_jobs(self):
        attendee = Attendee.objects.create(event=self.event, phone_number="+27123456789")
        Job.objects.create(event=self.event, attendee=attendee, status=JobStatus.PENDING)
        Job.objects.create(event=self.event, attendee=attendee, status=JobStatus.DONE)
        self.client.force_login(self.user)

        response = self.client.get(f"/api/events/mine/{self.event.id}/attendees/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["phone_last_four"], "6789")
        self.assertNotIn("phone_number", response.data[0])
        self.assertEqual(response.data[0]["generation_count"], 2)

    def test_organizer_can_block_and_unblock_owned_attendee(self):
        attendee = Attendee.objects.create(event=self.event, phone_number="+27123456789")
        self.client.force_login(self.user)

        blocked = self.client.patch(
            f"/api/events/mine/{self.event.id}/attendees/{attendee.id}/status/",
            {"status": AttendeeStatus.BLOCKED},
            format="json",
        )
        self.assertEqual(blocked.status_code, 200)
        self.assertEqual(blocked.data["status"], AttendeeStatus.BLOCKED)

        unblocked = self.client.patch(
            f"/api/events/mine/{self.event.id}/attendees/{attendee.id}/status/",
            {"status": AttendeeStatus.ACTIVE},
            format="json",
        )
        self.assertEqual(unblocked.status_code, 200)

    @override_settings(EVENT_RESOLUTION_RATE_PER_HOUR=1)
    def test_event_resolution_is_rate_limited(self):
        cache.clear()

        first = self.client.get(f"/api/events/resolve/{self.event.public_token}/")
        second = self.client.get(f"/api/events/resolve/{self.event.public_token}/")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
