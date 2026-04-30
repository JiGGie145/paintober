from django.urls import path

from .views import PaletteListView

urlpatterns = [
    path("", PaletteListView.as_view(), name="palette-list"),
]
