from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.proposals.models import Proposal


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        next_week = today + timedelta(days=7)

        proposals_by_status = list(
            Proposal.objects.values("status").annotate(total=Count("id")).order_by("status")
        )
        proposals_by_responsible = list(
            Proposal.objects.values("responsible__username").annotate(total=Count("id")).order_by("-total")
        )
        recent_audits = list(
            AuditLog.objects.select_related("user").values(
                "action",
                "model_name",
                "description",
                "created_at",
                "user__username",
            )[:8]
        )

        data = {
            "total_clients": Client.objects.count(),
            "total_proposals": Proposal.objects.count(),
            "proposals_draft": Proposal.objects.filter(status=Proposal.Status.DRAFT).count(),
            "proposals_in_review": Proposal.objects.filter(status=Proposal.Status.IN_REVIEW).count(),
            "proposals_approved": Proposal.objects.filter(status=Proposal.Status.APPROVED).count(),
            "proposals_expiring": Proposal.objects.exclude(
                status__in=[Proposal.Status.APPROVED, Proposal.Status.REJECTED, Proposal.Status.EXPIRED]
            ).filter(due_date__range=(today, next_week)).count(),
            "proposals_by_status": proposals_by_status,
            "proposals_by_responsible": proposals_by_responsible,
            "recent_audits": recent_audits,
        }
        return Response(data)