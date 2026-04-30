from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import PaintSet
from .serializers import PaintSetSerializer


class PaletteListView(ListAPIView):
    queryset = PaintSet.objects.prefetch_related("colors").all()
    serializer_class = PaintSetSerializer
    permission_classes = [AllowAny]
    pagination_class = None
