from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.proposals.forms import ProposalStatusForm
from apps.proposals.models import Proposal, ProposalStatusHistory

User = get_user_model()


class BaseProposalTestData(TestCase):
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


class ProposalStatusFormTests(BaseProposalTestData):
    def test_advisor_form_excludes_restricted_statuses(self):
        form = ProposalStatusForm(user=self.advisor, proposal=self.proposal)
        statuses = [value for value, _label in form.fields["status"].choices]

        self.assertNotIn(Proposal.Status.APPROVED, statuses)
        self.assertNotIn(Proposal.Status.REJECTED, statuses)
        self.assertNotIn(Proposal.Status.EXPIRED, statuses)
        self.assertIn(Proposal.Status.DRAFT, statuses)
        self.assertIn(Proposal.Status.SENT, statuses)
        self.assertIn(Proposal.Status.IN_REVIEW, statuses)

    def test_supervisor_form_includes_approved_and_rejected(self):
        form = ProposalStatusForm(user=self.supervisor, proposal=self.proposal)
        statuses = [value for value, _label in form.fields["status"].choices]

        self.assertIn(Proposal.Status.APPROVED, statuses)
        self.assertIn(Proposal.Status.REJECTED, statuses)
        self.assertNotIn(Proposal.Status.EXPIRED, statuses)


class ProposalStatusUpdateTests(BaseProposalTestData):
    def test_supervisor_can_approve_proposal(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse("proposal-change-status", args=[self.proposal.pk]),
            {
                "status": Proposal.Status.APPROVED,
                "comment": "Aprobación válida desde supervisor.",
            },
        )

        self.proposal.refresh_from_db()

        self.assertEqual(response.status_code, 302)
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

class ProposalExportCsvTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="proposal_export_user",
            email="proposal_export@example.com",
            password="Test12345!",
        )
        self.user.user_permissions.add(Permission.objects.get(codename="view_proposal"))

        self.client_obj = Client.objects.create(
            business_name="Cliente Export Proposals SAC",
            document_number="20444555666",
            email="cliente-export-proposals@example.com",
            phone="988777666",
            address="Lima",
            status=Client.Status.ACTIVE,
            created_by=self.user,
        )

        Proposal.objects.create(
            client=self.client_obj,
            title="Propuesta En Revision",
            description="Demo export CSV",
            responsible=self.user,
            estimated_amount=15000,
            due_date=timezone.localdate(),
            status=Proposal.Status.IN_REVIEW,
            created_by=self.user,
        )

        Proposal.objects.create(
            client=self.client_obj,
            title="Propuesta Aprobada",
            description="Demo export CSV",
            responsible=self.user,
            estimated_amount=25000,
            due_date=timezone.localdate(),
            status=Proposal.Status.APPROVED,
            created_by=self.user,
        )

    def test_export_proposals_csv_respects_filters(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("proposal-export-csv"),
            {"status": Proposal.Status.IN_REVIEW},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])

        content = response.content.decode("utf-8-sig")
        self.assertIn("Propuesta En Revision", content)
        self.assertNotIn("Propuesta Aprobada", content)