import re

from rest_framework import serializers

from .models import Attendee, Event, OrganizerProfile


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if OrganizerProfile.objects.filter(user__email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class OrganizerSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="user_id")
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")


class EventSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="public_token", read_only=True)
    accepts_new_generations = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "name", "event_date", "token", "status", "otp_required",
            "max_kits_per_attendee", "branding", "accepts_new_generations", "is_expired",
        ]
        read_only_fields = ["id", "token", "status", "accepts_new_generations", "is_expired"]


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["name", "event_date", "otp_required", "max_kits_per_attendee", "branding", "allocated_credits"]

    allocated_credits = serializers.IntegerField(min_value=1, write_only=True)

    def validate_max_kits_per_attendee(self, value):
        if value < 1:
            raise serializers.ValidationError("The attendee kit limit must be at least one.")
        return value


class EventPublicSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="public_token")
    accepts_new_generations = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = ["name", "event_date", "token", "status", "otp_required", "accepts_new_generations", "is_expired", "branding"]


class AttendeeEntrySerializer(serializers.Serializer):
    event_token = serializers.CharField(max_length=64)
    phone_number = serializers.CharField(max_length=32)

    def validate_phone_number(self, value):
        normalized = re.sub(r"[^0-9+]", "", value).strip()
        if normalized.startswith("00"):
            normalized = "+" + normalized[2:]
        if normalized.startswith("+"):
            digits = normalized[1:]
        else:
            digits = normalized
        if not digits.isdigit() or not 7 <= len(digits) <= 15:
            raise serializers.ValidationError("Enter a valid phone number.")
        return f"+{digits}"


class AttendeeContextSerializer(serializers.Serializer):
    attendee_id = serializers.IntegerField()
    event = EventPublicSerializer()


class AttendeeActivitySerializer(serializers.ModelSerializer):
    phone_last_four = serializers.SerializerMethodField()
    generation_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Attendee
        fields = ["id", "phone_last_four", "status", "generation_count", "created_at", "updated_at"]
        read_only_fields = fields

    def get_phone_last_four(self, obj):
        return obj.phone_number[-4:]
