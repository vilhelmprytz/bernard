from rest_framework import viewsets

from .serializers import DomainSerializer
from .models import Domain


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all().order_by("domain")
    serializer_class = DomainSerializer
