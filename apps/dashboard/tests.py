from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.proposals.models import Proposal

User = get_user_model()


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard_user",
            email="dashboard@example.com",
            password="Test12345!",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard-home"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_shows_summary_metrics(self):
        self.client.force_login(self.user)

        client = Client.objects.create(
            business_name="Cliente Dashboard SAC",
            document_number="20999999991",
            email="cliente-dashboard@example.com",
            phone="999999999",
            address="Huancayo",
            status=Client.Status.ACTIVE,
            created_by=self.user,
        )

        Proposal.objects.create(
            client=client,
            title="Propuesta por vencer",
            description="Demo",
            responsible=self.user,
            estimated_amount=Decimal("15000.00"),
            due_date=timezone.localdate() + timedelta(days=3),
            status=Proposal.Status.IN_REVIEW,
            created_by=self.user,
        )

        Proposal.objects.create(
            client=client,
            title="Propuesta aprobada",
            description="Demo",
            responsible=self.user,
            estimated_amount=Decimal("20000.00"),
            due_date=timezone.localdate() + timedelta(days=20),
            status=Proposal.Status.APPROVED,
            created_by=self.user,
        )

        AuditLog.objects.create(
            user=self.user,
            action=AuditLog.Action.CREATE,
            model_name="cliente",
            object_id=str(client.pk),
            description="Registro de prueba",
        )

        response = self.client.get(reverse("dashboard-home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_clients"], 1)
        self.assertEqual(response.context["total_proposals"], 2)
        self.assertEqual(response.context["proposals_in_review"], 1)
        self.assertEqual(response.context["proposals_approved"], 1)
        self.assertEqual(response.context["proposals_expiring"], 1)
        self.assertEqual(len(response.context["expiring_proposals"]), 1)