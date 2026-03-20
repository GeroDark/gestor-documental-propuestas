from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.audit.services import log_audit

from .models import Comment, Proposal, ProposalStatusHistory
from .serializers import CommentSerializer, ProposalSerializer


class ProposalViewSet(ModelViewSet):
    queryset = Proposal.objects.select_related("client", "responsible", "created_by").all().order_by("-created_at")
    serializer_class = ProposalSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["status", "responsible", "client"]
    search_fields = ["title", "description", "client__business_name"]
    ordering_fields = ["created_at", "due_date", "estimated_amount"]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        ProposalStatusHistory.objects.create(
            proposal=instance,
            previous_status="",
            new_status=instance.status,
            comment="Creación inicial de la propuesta desde la API.",
            changed_by=self.request.user,
        )
        log_audit(
            user=self.request.user,
            action="create",
            instance=instance,
            description=f"Se creó la propuesta '{instance.title}' desde la API.",
        )

    def perform_update(self, serializer):
        old_status = self.get_object().status
        instance = serializer.save()

        if old_status != instance.status:
            ProposalStatusHistory.objects.create(
                proposal=instance,
                previous_status=old_status,
                new_status=instance.status,
                comment="Cambio de estado desde actualización API.",
                changed_by=self.request.user,
            )
            log_audit(
                user=self.request.user,
                action="status_change",
                instance=instance,
                description=f"La propuesta '{instance.title}' cambió de estado de '{old_status}' a '{instance.status}' desde la API.",
            )

        log_audit(
            user=self.request.user,
            action="update",
            instance=instance,
            description=f"Se actualizó la propuesta '{instance.title}' desde la API.",
        )

    @action(detail=True, methods=["post"], permission_classes=[DjangoModelPermissions])
    def change_status(self, request, pk=None):
        proposal = self.get_object()

        class StatusSerializer(serializers.Serializer):
            status = serializers.ChoiceField(choices=Proposal.Status.choices)
            comment = serializers.CharField(required=False, allow_blank=True)

        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        comment = serializer.validated_data.get("comment", "")
        previous_status = proposal.status

        if new_status in {Proposal.Status.APPROVED, Proposal.Status.REJECTED}:
            is_allowed = (
                request.user.groups.filter(name="Administrador").exists()
                or request.user.groups.filter(name="Supervisor").exists()
            )
            if not is_allowed:
                return Response(
                    {"detail": "No tienes permiso para aprobar o rechazar propuestas."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if previous_status != new_status:
            proposal.status = new_status
            proposal.save(update_fields=["status", "updated_at"])

            ProposalStatusHistory.objects.create(
                proposal=proposal,
                previous_status=previous_status,
                new_status=new_status,
                comment=comment,
                changed_by=request.user,
            )

            log_audit(
                user=request.user,
                action="status_change",
                instance=proposal,
                description=f"La propuesta '{proposal.title}' cambió de estado de '{previous_status}' a '{new_status}' desde la API.",
            )

        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=["get", "post"], permission_classes=[DjangoModelPermissions])
    def comments(self, request, pk=None):
        proposal = self.get_object()

        if request.method == "GET":
            serializer = CommentSerializer(proposal.comments.all(), many=True)
            return Response(serializer.data)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = Comment.objects.create(
            proposal=proposal,
            user=request.user,
            content=serializer.validated_data["content"],
        )

        log_audit(
            user=request.user,
            action="comment",
            instance=proposal,
            description=f"Se agregó un comentario a la propuesta '{proposal.title}' desde la API.",
        )

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)