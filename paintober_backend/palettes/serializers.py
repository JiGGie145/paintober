from rest_framework import serializers

from .models import PaintColor, PaintSet


class PaintColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaintColor
        fields = ["name", "hex"]


class PaintSetSerializer(serializers.ModelSerializer):
    colors = PaintColorSerializer(many=True, read_only=True)

    class Meta:
        model = PaintSet
        fields = ["id", "name", "description", "paint_type", "tube_count", "colors"]
