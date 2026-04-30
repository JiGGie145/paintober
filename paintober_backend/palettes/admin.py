from django.contrib import admin

from .models import PaintColor, PaintSet


class PaintColorInline(admin.TabularInline):
    model = PaintColor
    extra = 0
    fields = ["name", "hex"]


@admin.register(PaintSet)
class PaintSetAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "paint_type", "tube_count"]
    list_filter = ["paint_type"]
    inlines = [PaintColorInline]
