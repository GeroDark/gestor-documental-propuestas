from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

from apps.audit.services import log_audit

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.select_related("created_by").all().order_by("-created_at")
    serializer_class = ClientSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["status"]
    search_fields = ["business_name", "document_number", "email"]
    ordering_fields = ["created_at", "business_name"]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_audit(
            user=self.request.user,
            action="create",
            instance=instance,
            description=f"Se creó el cliente '{instance.business_name}' desde la API.",
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        log_audit(
            user=self.request.user,
            action="update",
            instance=instance,
            description=f"Se actualizó el cliente '{instance.business_name}' desde la API.",
        )

    def perform_destroy(self, instance):
        log_audit(
            user=self.request.user,
            action="delete",
            instance=instance,
            description=f"Se eliminó el cliente '{instance.business_name}' desde la API.",
        )
        instance.delete()