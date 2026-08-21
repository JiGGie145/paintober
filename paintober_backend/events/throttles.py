import hashlib
import re

from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class EventResolutionThrottle(SimpleRateThrottle):
    scope = "event_resolution"

    def get_rate(self):
        return f"{getattr(settings, 'EVENT_RESOLUTION_RATE_PER_HOUR', 60)}/hour"

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class AttendeeEntryThrottle(SimpleRateThrottle):
    scope = "attendee_entry"

    def get_rate(self):
        return f"{getattr(settings, 'ATTENDEE_ENTRY_RATE_PER_HOUR', 10)}/hour"

    def get_cache_key(self, request, view):
        token = str(request.data.get("event_token", ""))
        phone = re.sub(r"\D", "", str(request.data.get("phone_number", "")))[:3]
        bucket = hashlib.sha256(f"{token}:{phone}".encode()).hexdigest()[:24]
        return self.cache_format % {"scope": self.scope, "ident": f"{self.get_ident(request)}:{bucket}"}