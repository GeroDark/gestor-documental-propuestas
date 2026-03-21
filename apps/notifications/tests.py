from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.proposals.models import Proposal, ProposalStatusHistory

User = get_user_model()


class ProposalDeadlineCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="deadline_admin",
            email="deadline_admin@example.com",
            password="Test12345!",
        )

        self.client_obj = Client.objects.create(
            business_name="Cliente Alertas SAC",
            document_number="20555111222",
            email="cliente-alertas@example.com",
            phone="999555111",
            address="Huancayo",
            status=Client.Status.ACTIVE,
            created_by=self.user,
        )

        self.expiring_proposal = Proposal.objects.create(
            client=self.client_obj,
            title="Propuesta por vencer",
            description="Demo de propuesta próxima a vencer.",
            responsible=self.user,
            estimated_amount=Decimal("18000.00"),
            due_date=timezone.localdate() + timedelta(days=3),
            status=Proposal.Status.SENT,
            created_by=self.user,
        )

        self.overdue_proposal = Proposal.objects.create(
            client=self.client_obj,
            title="Propuesta vencida pendiente",
            description="Demo de propuesta ya vencida.",
            responsible=self.user,
            estimated_amount=Decimal("22000.00"),
            due_date=timezone.localdate() - timedelta(days=2),
            status=Proposal.Status.IN_REVIEW,
            created_by=self.user,
        )

        self.approved_proposal = Proposal.objects.create(
            client=self.client_obj,
            title="Propuesta aprobada",
            description="No debe entrar en alertas.",
            responsible=self.user,
            estimated_amount=Decimal("30000.00"),
            due_date=timezone.localdate() + timedelta(days=1),
            status=Proposal.Status.APPROVED,
            created_by=self.user,
        )

    def test_command_lists_expiring_and_overdue_proposals(self):
        output = StringIO()

        call_command("check_proposal_deadlines", stdout=output)

        content = output.getvalue()

        self.assertIn("Propuestas por vencer en los próximos 7 días: 1", content)
        self.assertIn("Propuesta por vencer", content)
        self.assertIn("Propuestas vencidas pendientes de marcar: 1", content)
        self.assertIn("Propuesta vencida pendiente", content)
        self.assertNotIn("Propuesta aprobada", content)

        self.overdue_proposal.refresh_from_db()
        self.assertEqual(self.overdue_proposal.status, Proposal.Status.IN_REVIEW)

    def test_command_marks_overdue_proposals_as_expired(self):
        output = StringIO()

        call_command(
            "check_proposal_deadlines",
            "--mark-expired",
            "--changed-by",
            self.user.username,
            stdout=output,
        )

        content = output.getvalue()

        self.overdue_proposal.refresh_from_db()
        self.expiring_proposal.refresh_from_db()
        self.approved_proposal.refresh_from_db()

        self.assertEqual(self.overdue_proposal.status, Proposal.Status.EXPIRED)
        self.assertEqual(self.expiring_proposal.status, Proposal.Status.SENT)
        self.assertEqual(self.approved_proposal.status, Proposal.Status.APPROVED)

        self.assertTrue(
            ProposalStatusHistory.objects.filter(
                proposal=self.overdue_proposal,
                previous_status=Proposal.Status.IN_REVIEW,
                new_status=Proposal.Status.EXPIRED,
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.STATUS_CHANGE,
                object_id=str(self.overdue_proposal.pk),
            ).exists()
        )

        self.assertIn("Se marcaron 1 propuesta(s) como vencida(s).", content)