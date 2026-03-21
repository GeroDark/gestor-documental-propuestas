from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.proposals.models import Proposal, ProposalStatusHistory

User = get_user_model()


class ProposalStatusUpdateTests(TestCase):
    def setUp(self):
        self.advisor = User.objects.create_user(
            username="asesor_test",
            email="asesor_test@example.com",
            password="Test12345!",
        )
        self.supervisor = User.objects.create_user(
            username="supervisor_test",
            email="supervisor_test@example.com",
            password="Test12345!",
        )

        supervisor_group, _ = Group.objects.get_or_create(name="Supervisor")
        self.supervisor.groups.add(supervisor_group)

        change_permission = Permission.objects.get(codename="change_proposal")
        self.advisor.user_permissions.add(change_permission)
        self.supervisor.user_permissions.add(change_permission)

        self.client_obj = Client.objects.create(
            business_name="Cliente Proposals SAC",
            document_number="20999999992",
            email="cliente-proposals@example.com",
            phone="988888888",
            address="Lima",
            status=Client.Status.ACTIVE,
            created_by=self.advisor,
        )

        self.proposal = Proposal.objects.create(
            client=self.client_obj,
            title="Propuesta estado prueba",
            description="Demo",
            responsible=self.advisor,
            estimated_amount=Decimal("30000.00"),
            due_date=timezone.localdate() + timedelta(days=10),
            status=Proposal.Status.SENT,
            created_by=self.advisor,
        )

    def test_advisor_cannot_approve_proposal(self):
        self.client.force_login(self.advisor)

        response = self.client.post(
            reverse("proposal-change-status", args=[self.proposal.pk]),
            {
                "status": Proposal.Status.APPROVED,
                "comment": "Intento de aprobación sin permisos de grupo.",
            },
            follow=True,
        )

        self.proposal.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.proposal.status, Proposal.Status.SENT)
        self.assertEqual(
            ProposalStatusHistory.objects.filter(proposal=self.proposal).count(),
            0,
        )
        self.assertFalse(
            AuditLog.objects.filter(
                action=AuditLog.Action.STATUS_CHANGE,
                object_id=str(self.proposal.pk),
            ).exists()
        )

    def test_supervisor_can_approve_proposal(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse("proposal-change-status", args=[self.proposal.pk]),
            {
                "status": Proposal.Status.APPROVED,
                "comment": "Aprobación válida desde supervisor.",
            },
            follow=True,
        )

        self.proposal.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.proposal.status, Proposal.Status.APPROVED)
        self.assertTrue(
            ProposalStatusHistory.objects.filter(
                proposal=self.proposal,
                previous_status=Proposal.Status.SENT,
                new_status=Proposal.Status.APPROVED,
            ).exists()
        )
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.STATUS_CHANGE,
                object_id=str(self.proposal.pk),
            ).exists()
        )