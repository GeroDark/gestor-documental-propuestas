from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

from apps.audit.services import log_audit

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(ModelViewSet):
    queryset = Document.objects.select_related("client", "proposal", "uploaded_by").all().order_by("-uploaded_at")
    serializer_class = DocumentSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["document_type", "client", "proposal"]
    search_fields = ["original_name", "client__business_name", "proposal__title"]
    ordering_fields = ["uploaded_at", "original_name"]

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get("file")
        instance = serializer.save(
            uploaded_by=self.request.user,
            original_name=uploaded_file.name if uploaded_file else "",
        )
        log_audit(
            user=self.request.user,
            action="create",
            instance=instance,
            description=f"Se subió el documento '{instance.original_name}' desde la API.",
        )