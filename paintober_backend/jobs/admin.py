from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "retry_count", "user", "session_key", "created_at", "error_message_short"]
    list_filter = ["status"]
    search_fields = ["id", "user__username", "session_key"]
    readonly_fields = [
        "id", "user", "session_key", "status", "retry_count", "error_message",
        "parameters", "input_file", "output_outline", "output_color",
        "output_palette", "output_zip", "created_at", "updated_at",
    ]
    ordering = ["-created_at"]

    @admin.display(description="Error (truncated)")
    def error_message_short(self, obj):
        if obj.error_message:
            return obj.error_message[:80]
        return ""
