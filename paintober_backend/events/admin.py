from django.contrib import admin

from .models import Attendee, CreditLedgerEntry, CreditReservation, Event, OrganizerProfile


@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    search_fields = ["user__email", "user__username"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "organizer", "event_date", "status", "public_token"]
    list_filter = ["status", "event_date"]
    search_fields = ["name", "public_token", "organizer__user__email"]
    readonly_fields = ["id", "public_token", "created_at", "updated_at"]


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ["event", "phone_number", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["phone_number", "event__name"]


@admin.register(CreditLedgerEntry)
class CreditLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ["organizer", "event", "entry_type", "quantity", "created_at"]
    list_filter = ["entry_type"]
    search_fields = ["organizer__user__email", "event__name", "note"]
    readonly_fields = ["id", "created_at", "reference"]


@admin.register(CreditReservation)
class CreditReservationAdmin(admin.ModelAdmin):
    list_display = ["event", "attendee", "quantity", "status", "created_at"]
    list_filter = ["status"]
    readonly_fields = ["id", "created_at", "updated_at"]
