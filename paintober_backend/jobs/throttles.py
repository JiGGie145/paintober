from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class JobCreationThrottle(SimpleRateThrottle):
    """Limit job creation to settings.JOB_RATE_LIMIT_PER_HOUR per user/session."""

    scope = "job_creation"

    def get_rate(self):
        limit = getattr(settings, "JOB_RATE_LIMIT_PER_HOUR", 20)
        return f"{limit}/hour"

    def get_cache_key(self, request, view):
        attendee_context = request.session.get("paintober_attendee_context")
        if attendee_context:
            # Match job authorization: an active attendee context remains
            # session-scoped even when the browser also sends a JWT.
            ident = f"session_{request.session.session_key or 'anon'}"
        elif request.user and request.user.is_authenticated:
            ident = f"user_{request.user.pk}"
        else:
            ident = f"session_{request.session.session_key or 'anon'}"
        return self.cache_format % {"scope": self.scope, "ident": ident}
