from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
from django.views.generic import TemplateView

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.proposals.models import Proposal


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()
        next_week = today + timedelta(days=7)

        proposals_by_status = (
            Proposal.objects.values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

        proposals_by_responsible = (
            Proposal.objects.values("responsible__username")
            .annotate(total=Count("id"))
            .order_by("-total", "responsible__username")
        )

        expiring_proposals = (
            Proposal.objects.select_related("client", "responsible")
            .exclude(status__in=[Proposal.Status.APPROVED, Proposal.Status.REJECTED, Proposal.Status.EXPIRED])
            .filter(due_date__range=(today, next_week))
            .order_by("due_date")[:5]
        )

        recent_audits = AuditLog.objects.select_related("user")[:8]

        context.update(
            {
                "total_clients": Client.objects.count(),
                "total_proposals": Proposal.objects.count(),
                "proposals_draft": Proposal.objects.filter(status=Proposal.Status.DRAFT).count(),
                "proposals_in_review": Proposal.objects.filter(status=Proposal.Status.IN_REVIEW).count(),
                "proposals_approved": Proposal.objects.filter(status=Proposal.Status.APPROVED).count(),
                "proposals_expiring": expiring_proposals.count(),
                "proposals_by_status": proposals_by_status,
                "proposals_by_responsible": proposals_by_responsible,
                "expiring_proposals": expiring_proposals,
                "recent_audits": recent_audits,
            }
        )
        return context