from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.clients.models import Client
from apps.documents.models import Document
from apps.proposals.models import Proposal


class Command(BaseCommand):
    help = "Crea los grupos y permisos iniciales del sistema"

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="Administrador")
        advisor_group, _ = Group.objects.get_or_create(name="Asesor comercial")
        supervisor_group, _ = Group.objects.get_or_create(name="Supervisor")

        client_ct = ContentType.objects.get_for_model(Client)
        proposal_ct = ContentType.objects.get_for_model(Proposal)
        document_ct = ContentType.objects.get_for_model(Document)

        admin_permissions = Permission.objects.filter(
            content_type__in=[client_ct, proposal_ct, document_ct]
        )

        advisor_permissions = Permission.objects.filter(
            content_type__in=[client_ct, proposal_ct, document_ct],
            codename__in=[
                "add_client", "change_client", "view_client",
                "add_proposal", "change_proposal", "view_proposal",
                "add_document", "change_document", "view_document",
            ],
        )

        supervisor_permissions = Permission.objects.filter(
            content_type__in=[client_ct, proposal_ct, document_ct],
            codename__in=[
                "view_client",
                "view_proposal", "change_proposal",
                "view_document",
            ],
        )

        admin_group.permissions.set(admin_permissions)
        advisor_group.permissions.set(advisor_permissions)
        supervisor_group.permissions.set(supervisor_permissions)

        self.stdout.write(self.style.SUCCESS("Grupos y permisos creados correctamente."))