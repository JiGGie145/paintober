from drf_spectacular.utils import extend_schema_field
from django.conf import settings
from rest_framework import serializers

from .models import Job, JobStatus


class DownloadUrlsSerializer(serializers.Serializer):
    outline = serializers.URLField(required=False, allow_null=True)
    color = serializers.URLField(required=False, allow_null=True)
    palette = serializers.URLField(required=False, allow_null=True)
    zip = serializers.URLField(required=False, allow_null=True)


class JobCreateResponseSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=JobStatus.choices)


class JobCreateSerializer(serializers.Serializer):
    image = serializers.ImageField(write_only=True)
    kit_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    event_id = serializers.UUIDField(required=False, allow_null=True)
    style = serializers.ChoiceField(choices=["realistic", "cartoonish"], default="realistic")
    output_mode = serializers.ChoiceField(
        choices=["paint_by_numbers", "outline_only"],
        default="paint_by_numbers",
    )
    # Pipeline parameters — all optional, pipeline defaults apply
    k_colors = serializers.IntegerField(min_value=2, max_value=32, required=False)
    line_thickness = serializers.IntegerField(min_value=1, max_value=10, required=False)
    smooth_method = serializers.ChoiceField(
        choices=["meanshift", "bilateral", "gaussian", "none"],
        required=False,
    )
    blur_sigma = serializers.FloatField(min_value=0.0, max_value=10.0, required=False)
    min_region_pct = serializers.FloatField(min_value=0.0, max_value=1.0, required=False)
    no_merge = serializers.BooleanField(required=False)
    # BYOP
    use_user_palette = serializers.BooleanField(required=False)
    user_palette_mode = serializers.ChoiceField(choices=["rgb", "hex"], required=False)
    user_palette_rgb = serializers.ListField(
        child=serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=255), min_length=3, max_length=3),
        required=False,
    )
    user_palette_hex = serializers.ListField(
        child=serializers.CharField(max_length=7),
        required=False,
    )
    allow_color_reuse = serializers.BooleanField(required=False)

    PARAM_FIELDS = [
        "style", "output_mode",
        "k_colors", "line_thickness", "smooth_method", "blur_sigma",
        "min_region_pct", "no_merge", "use_user_palette",
        "user_palette_mode", "user_palette_rgb", "user_palette_hex",
        "allow_color_reuse",
    ]

    def extract_params(self) -> dict:
        return {
            key: self.validated_data[key]
            for key in self.PARAM_FIELDS
            if key in self.validated_data
        }

    def validate(self, attrs):
        style = attrs.get("style", "realistic")
        output_mode = attrs.get("output_mode", "paint_by_numbers")
        if style == "cartoonish" and not settings.VERTEX_AI_ENABLED:
            raise serializers.ValidationError(
                {"style": "The cartoonish style is not currently available."}
            )
        if style == "cartoonish" and output_mode != "outline_only":
            raise serializers.ValidationError(
                {"output_mode": "Cartoonish jobs must use outline_only output."}
            )
        return attrs


class JobStatusSerializer(serializers.ModelSerializer):
    download_urls = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id", "status", "retry_count", "error_message",
            "kit_name", "parameters", "created_at", "updated_at", "download_urls",
        ]
        read_only_fields = fields

    @extend_schema_field(DownloadUrlsSerializer)
    def get_download_urls(self, obj):
        if obj.status != "done":
            return None
        request = self.context.get("request")
        if request is None:
            return None
        from .views import _signed_url
        urls = {"outline": _signed_url(request, obj, "outline")}
        if obj.output_color:
            urls["color"] = _signed_url(request, obj, "color")
        if obj.output_palette:
            urls["palette"] = _signed_url(request, obj, "palette")
        if obj.output_zip:
            urls["zip"] = _signed_url(request, obj, "zip")
        return urls


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "status", "retry_count", "kit_name", "created_at", "updated_at"]
        read_only_fields = fields
