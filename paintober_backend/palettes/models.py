from django.db import models


class PaintSet(models.Model):
    id = models.SlugField(primary_key=True, max_length=60)
    name = models.CharField(max_length=120)
    description = models.TextField()
    paint_type = models.CharField(max_length=50)
    tube_count = models.IntegerField()

    class Meta:
        ordering = ["paint_type", "tube_count", "id"]

    def __str__(self) -> str:
        return self.name


class PaintColor(models.Model):
    paint_set = models.ForeignKey(PaintSet, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=80)
    hex = models.CharField(max_length=7)

    class Meta:
        order_with_respect_to = "paint_set"

    def __str__(self) -> str:
        return f"{self.name} ({self.hex})"
