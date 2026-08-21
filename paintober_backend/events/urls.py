from django.urls import path

from .views import (
    AdminCreditGrantView,
    EventEnterView,
    EventResolveView,
    OrganizerCreditBalanceView,
    OrganizerEventDetailView,
    OrganizerEventKitsView,
    OrganizerEventListCreateView,
    OrganizerAttendeeActivityView,
    OrganizerAttendeeBlockView,
)

urlpatterns = [
    path("credits/", OrganizerCreditBalanceView.as_view(), name="credit-balance"),
    path("credits/grant/", AdminCreditGrantView.as_view(), name="credit-grant"),
    path("mine/", OrganizerEventListCreateView.as_view(), name="organizer-events"),
    path("mine/<uuid:event_id>/", OrganizerEventDetailView.as_view(), name="organizer-event-detail"),
    path("mine/<uuid:event_id>/kits/", OrganizerEventKitsView.as_view(), name="organizer-event-kits"),
    path("mine/<uuid:event_id>/attendees/", OrganizerAttendeeActivityView.as_view(), name="organizer-attendee-activity"),
    path("mine/<uuid:event_id>/attendees/<int:attendee_id>/status/", OrganizerAttendeeBlockView.as_view(), name="organizer-attendee-status"),
    path("resolve/<str:event_token>/", EventResolveView.as_view(), name="event-resolve"),
    path("enter/", EventEnterView.as_view(), name="event-enter"),
]
