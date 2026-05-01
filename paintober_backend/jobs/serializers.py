from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Job, JobStatus


class DownloadUrlsSerializer(serializers.Serializer):
    outline = serializers.URLField()
    color = serializers.URLField()
    palette = serializers.URLField()
    zip = serializers.URLField()


class JobCreateResponseSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=JobStatus.choices)


class JobCreateSerializer(serializers.Serializer):
    image = serializers.ImageField(write_only=True)
    # Pipeline parameters — all optional, pipeline defaults apply
    k_colors = serializers.IntegerField(min_value=2, max_value=32, required=False)
    min_region_area = serializers.IntegerField(min_value=1, required=False)
    contour_epsilon = serializers.FloatField(min_value=0.0, max_value=0.05, required=False)
    line_thickness = serializers.IntegerField(min_value=1, max_value=10, required=False)
    apply_gaussian = serializers.BooleanField(required=False)
    min_label_spacing = serializers.IntegerField(min_value=1, max_value=100, required=False)
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
        "k_colors", "min_region_area", "contour_epsilon", "line_thickness",
        "apply_gaussian", "min_label_spacing", "use_user_palette",
        "user_palette_mode", "user_palette_rgb", "user_palette_hex",
        "allow_color_reuse",
    ]

    def extract_params(self) -> dict:
        return {
            key: self.validated_data[key]
            for key in self.PARAM_FIELDS
            if key in self.validated_data
        }


class JobStatusSerializer(serializers.ModelSerializer):
    download_urls = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id", "status", "retry_count", "error_message",
            "parameters", "created_at", "updated_at", "download_urls",
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
        return {
            "outline": _signed_url(request, obj, "outline"),
            "color": _signed_url(request, obj, "color"),
            "palette": _signed_url(request, obj, "palette"),
            "zip": _signed_url(request, obj, "zip"),
        }


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "status", "retry_count", "created_at", "updated_at"]
        read_only_fields = fields
