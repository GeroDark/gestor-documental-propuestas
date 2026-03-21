from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.clients.models import Client
from apps.documents.models import Document
from apps.proposals.models import Comment, Proposal, ProposalStatusHistory

User = get_user_model()

DEMO_PASSWORD = "Demo12345!"

DEMO_USERNAMES = ["admin_demo", "asesor_demo", "supervisor_demo"]

DEMO_CLIENTS = [
    {
        "business_name": "TechSolutions Andinas S.A.C.",
        "document_number": "20601234567",
        "email": "contacto@techsolutionsdemo.com",
        "phone": "999111222",
        "address": "Av. Javier Prado 1500, San Isidro",
        "status": Client.Status.ACTIVE,
        "notes": "Cliente demo orientado a servicios de digitalización y automatización.",
    },
    {
        "business_name": "Grupo Constructor del Centro S.A.C.",
        "document_number": "20567890123",
        "email": "licitaciones@constructoracentro.com",
        "phone": "988222333",
        "address": "Av. Mariscal Castilla 120, Huancayo",
        "status": Client.Status.ACTIVE,
        "notes": "Cliente demo del rubro construcción e infraestructura.",
    },
    {
        "business_name": "Inversiones Logísticas del Perú S.A.C.",
        "document_number": "20456789012",
        "email": "operaciones@logisticaperu.com",
        "phone": "977333444",
        "address": "Av. Argentina 845, Lima",
        "status": Client.Status.ACTIVE,
        "notes": "Cliente demo con necesidades de archivo y trazabilidad documental.",
    },
    {
        "business_name": "Comercial Huanca E.I.R.L.",
        "document_number": "20111111111",
        "email": "gerencia@comercialhuanca.com",
        "phone": "966444555",
        "address": "Jr. Real 510, Huancayo",
        "status": Client.Status.INACTIVE,
        "notes": "Cliente demo inactivo para mostrar variedad de estados.",
    },
]

DEMO_PROPOSAL_TITLES = [
    "Propuesta de digitalización documental 2026",
    "Servicio de custodia documental - sede centro",
    "Renovación de contrato marco de archivo",
    "Implementación de flujo de aprobación interno",
    "Propuesta de reorganización de expedientes históricos",
    "Actualización de repositorio contractual 2025-2026",
]

DEMO_DOCUMENT_NAMES = [
    "propuesta_digitalizacion_2026.txt",
    "contrato_custodia_sede_centro.txt",
    "renovacion_contrato_marco.txt",
    "anexo_flujo_aprobacion.txt",
    "informe_expedientes_historicos.txt",
    "carta_fianza_techsolutions.txt",
]


class Command(BaseCommand):
    help = "Crea datos demo para mostrar el sistema en portafolio, entrevistas y pruebas locales."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina primero los datos demo anteriores y los vuelve a crear.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.reset_demo_data()

        users = self.create_users_and_groups()
        clients = self.create_clients(users)
        proposals = self.create_proposals(users, clients)
        self.create_status_history(users, proposals)
        self.create_comments(users, proposals)
        self.create_documents(users, clients, proposals)

        self.stdout.write(self.style.SUCCESS("Datos demo creados correctamente."))
        self.stdout.write(f"Usuarios demo: {', '.join(DEMO_USERNAMES)}")
        self.stdout.write(f"Contraseña común: {DEMO_PASSWORD}")

    def reset_demo_data(self):
        demo_documents = Document.objects.filter(original_name__in=DEMO_DOCUMENT_NAMES)
        for document in demo_documents:
            if document.file:
                document.file.delete(save=False)
        demo_documents.delete()

        Proposal.objects.filter(title__in=DEMO_PROPOSAL_TITLES).delete()
        Client.objects.filter(
            document_number__in=[client["document_number"] for client in DEMO_CLIENTS]
        ).delete()
        User.objects.filter(username__in=DEMO_USERNAMES).delete()

        self.stdout.write(self.style.WARNING("Datos demo anteriores eliminados."))

    def create_users_and_groups(self):
        admin_group, _ = Group.objects.get_or_create(name="Administrador")
        advisor_group, _ = Group.objects.get_or_create(name="Asesor comercial")
        supervisor_group, _ = Group.objects.get_or_create(name="Supervisor")

        users = {
            "admin": self.upsert_user(
                username="admin_demo",
                email="admin_demo@example.com",
                first_name="Admin",
                last_name="Demo",
                group=admin_group,
                is_staff=True,
                is_superuser=True,
            ),
            "advisor": self.upsert_user(
                username="asesor_demo",
                email="asesor_demo@example.com",
                first_name="Asesor",
                last_name="Comercial",
                group=advisor_group,
            ),
            "supervisor": self.upsert_user(
                username="supervisor_demo",
                email="supervisor_demo@example.com",
                first_name="Supervisor",
                last_name="Demo",
                group=supervisor_group,
                is_staff=True,
            ),
        }

        return users

    def upsert_user(
        self,
        *,
        username,
        email,
        first_name,
        last_name,
        group,
        is_staff=False,
        is_superuser=False,
    ):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = True
        user.set_password(DEMO_PASSWORD)
        user.save()
        user.groups.set([group])

        return user

    def create_clients(self, users):
        created_clients = {}

        for item in DEMO_CLIENTS:
            client, _ = Client.objects.update_or_create(
                document_number=item["document_number"],
                defaults={
                    "business_name": item["business_name"],
                    "email": item["email"],
                    "phone": item["phone"],
                    "address": item["address"],
                    "status": item["status"],
                    "notes": item["notes"],
                    "created_by": users["advisor"],
                },
            )
            created_clients[item["document_number"]] = client

        return created_clients

    def create_proposals(self, users, clients):
        today = timezone.localdate()

        proposals_data = [
            {
                "key": "digitalizacion",
                "client": clients["20601234567"],
                "title": "Propuesta de digitalización documental 2026",
                "description": "Proyecto demo para digitalización, indexación y control documental.",
                "responsible": users["advisor"],
                "estimated_amount": Decimal("85000.00"),
                "due_date": today + timedelta(days=5),
                "status": Proposal.Status.IN_REVIEW,
                "created_by": users["advisor"],
            },
            {
                "key": "custodia",
                "client": clients["20567890123"],
                "title": "Servicio de custodia documental - sede centro",
                "description": "Servicio demo de organización, archivo y custodia para expedientes físicos.",
                "responsible": users["supervisor"],
                "estimated_amount": Decimal("120000.00"),
                "due_date": today + timedelta(days=15),
                "status": Proposal.Status.APPROVED,
                "created_by": users["advisor"],
            },
            {
                "key": "contrato_marco",
                "client": clients["20456789012"],
                "title": "Renovación de contrato marco de archivo",
                "description": "Renovación demo para servicio documental anual.",
                "responsible": users["advisor"],
                "estimated_amount": Decimal("46000.00"),
                "due_date": today + timedelta(days=3),
                "status": Proposal.Status.SENT,
                "created_by": users["advisor"],
            },
            {
                "key": "flujo_aprobacion",
                "client": clients["20111111111"],
                "title": "Implementación de flujo de aprobación interno",
                "description": "Propuesta demo para mejorar validaciones y trazabilidad interna.",
                "responsible": users["advisor"],
                "estimated_amount": Decimal("32000.00"),
                "due_date": today + timedelta(days=10),
                "status": Proposal.Status.DRAFT,
                "created_by": users["advisor"],
            },
            {
                "key": "expedientes_historicos",
                "client": clients["20456789012"],
                "title": "Propuesta de reorganización de expedientes históricos",
                "description": "Servicio demo de clasificación, depuración y reorganización histórica.",
                "responsible": users["supervisor"],
                "estimated_amount": Decimal("64000.00"),
                "due_date": today - timedelta(days=2),
                "status": Proposal.Status.REJECTED,
                "created_by": users["advisor"],
            },
            {
                "key": "repositorio_contractual",
                "client": clients["20601234567"],
                "title": "Actualización de repositorio contractual 2025-2026",
                "description": "Actualización demo de repositorio y estructura documental contractual.",
                "responsible": users["advisor"],
                "estimated_amount": Decimal("54000.00"),
                "due_date": today - timedelta(days=7),
                "status": Proposal.Status.EXPIRED,
                "created_by": users["advisor"],
            },
        ]

        created_proposals = {}

        for item in proposals_data:
            proposal, _ = Proposal.objects.update_or_create(
                client=item["client"],
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "responsible": item["responsible"],
                    "estimated_amount": item["estimated_amount"],
                    "due_date": item["due_date"],
                    "status": item["status"],
                    "created_by": item["created_by"],
                },
            )
            created_proposals[item["key"]] = proposal

        return created_proposals

    def create_status_history(self, users, proposals):
        history_rows = [
            (
                proposals["digitalizacion"],
                "",
                Proposal.Status.DRAFT,
                "Propuesta creada en borrador.",
                users["advisor"],
            ),
            (
                proposals["digitalizacion"],
                Proposal.Status.DRAFT,
                Proposal.Status.SENT,
                "Propuesta enviada al cliente.",
                users["advisor"],
            ),
            (
                proposals["digitalizacion"],
                Proposal.Status.SENT,
                Proposal.Status.IN_REVIEW,
                "Cliente solicitó ajustes en alcance y cronograma.",
                users["supervisor"],
            ),
            (
                proposals["custodia"],
                "",
                Proposal.Status.DRAFT,
                "Se generó propuesta inicial.",
                users["advisor"],
            ),
            (
                proposals["custodia"],
                Proposal.Status.DRAFT,
                Proposal.Status.SENT,
                "Se remitió propuesta para evaluación.",
                users["advisor"],
            ),
            (
                proposals["custodia"],
                Proposal.Status.SENT,
                Proposal.Status.APPROVED,
                "Cliente aprobó condiciones comerciales.",
                users["supervisor"],
            ),
            (
                proposals["contrato_marco"],
                "",
                Proposal.Status.DRAFT,
                "Borrador creado.",
                users["advisor"],
            ),
            (
                proposals["contrato_marco"],
                Proposal.Status.DRAFT,
                Proposal.Status.SENT,
                "Propuesta enviada, pendiente de respuesta.",
                users["advisor"],
            ),
            (
                proposals["flujo_aprobacion"],
                "",
                Proposal.Status.DRAFT,
                "Pendiente de validación interna antes del envío.",
                users["advisor"],
            ),
            (
                proposals["expedientes_historicos"],
                "",
                Proposal.Status.DRAFT,
                "Se registró propuesta inicial.",
                users["advisor"],
            ),
            (
                proposals["expedientes_historicos"],
                Proposal.Status.DRAFT,
                Proposal.Status.SENT,
                "Cliente recibió propuesta formal.",
                users["advisor"],
            ),
            (
                proposals["expedientes_historicos"],
                Proposal.Status.SENT,
                Proposal.Status.REJECTED,
                "El cliente decidió postergar el proyecto.",
                users["supervisor"],
            ),
            (
                proposals["repositorio_contractual"],
                "",
                Proposal.Status.DRAFT,
                "Borrador registrado.",
                users["advisor"],
            ),
            (
                proposals["repositorio_contractual"],
                Proposal.Status.DRAFT,
                Proposal.Status.SENT,
                "Propuesta enviada sin observaciones.",
                users["advisor"],
            ),
            (
                proposals["repositorio_contractual"],
                Proposal.Status.SENT,
                Proposal.Status.EXPIRED,
                "Se venció el plazo sin respuesta del cliente.",
                users["supervisor"],
            ),
        ]

        for proposal, previous_status, new_status, comment, changed_by in history_rows:
            ProposalStatusHistory.objects.get_or_create(
                proposal=proposal,
                previous_status=previous_status,
                new_status=new_status,
                comment=comment,
                changed_by=changed_by,
            )

    def create_comments(self, users, proposals):
        comments_data = [
            (
                proposals["digitalizacion"],
                users["advisor"],
                "El cliente pidió incluir una etapa de indexación avanzada.",
            ),
            (
                proposals["digitalizacion"],
                users["supervisor"],
                "Validar impacto en costos antes de enviar versión final.",
            ),
            (
                proposals["custodia"],
                users["advisor"],
                "Se coordinó visita técnica y quedó conforme con el alcance.",
            ),
            (
                proposals["contrato_marco"],
                users["advisor"],
                "Pendiente confirmación del área legal del cliente.",
            ),
            (
                proposals["flujo_aprobacion"],
                users["supervisor"],
                "Falta revisar permisos internos y trazabilidad del proceso.",
            ),
            (
                proposals["expedientes_historicos"],
                users["advisor"],
                "Cliente señaló que retomará este servicio el próximo trimestre.",
            ),
            (
                proposals["repositorio_contractual"],
                users["supervisor"],
                "Conviene reabrir esta oportunidad si el cliente reactiva presupuesto.",
            ),
        ]

        for proposal, user, content in comments_data:
            Comment.objects.get_or_create(
                proposal=proposal,
                user=user,
                content=content,
            )

    def create_documents(self, users, clients, proposals):
        self.upsert_document(
            client=clients["20601234567"],
            proposal=proposals["digitalizacion"],
            document_type=Document.DocumentType.COMMERCIAL_PROPOSAL,
            original_name="propuesta_digitalizacion_2026.txt",
            filename="propuesta_digitalizacion_2026.txt",
            content=(
                "Propuesta demo de digitalización documental 2026\n"
                "Cliente: TechSolutions Andinas S.A.C.\n"
                "Estado: En revisión\n"
                "Monto estimado: 85000.00\n"
            ),
            uploaded_by=users["advisor"],
        )

        self.upsert_document(
            client=clients["20567890123"],
            proposal=proposals["custodia"],
            document_type=Document.DocumentType.CONTRACT,
            original_name="contrato_custodia_sede_centro.txt",
            filename="contrato_custodia_sede_centro.txt",
            content=(
                "Contrato demo de custodia documental\n"
                "Cliente: Grupo Constructor del Centro S.A.C.\n"
                "Estado: Aprobada\n"
            ),
            uploaded_by=users["supervisor"],
        )

        self.upsert_document(
            client=clients["20456789012"],
            proposal=proposals["contrato_marco"],
            document_type=Document.DocumentType.REPORT,
            original_name="renovacion_contrato_marco.txt",
            filename="renovacion_contrato_marco.txt",
            content=(
                "Informe demo de renovación de contrato marco\n"
                "Cliente: Inversiones Logísticas del Perú S.A.C.\n"
            ),
            uploaded_by=users["advisor"],
        )

        self.upsert_document(
            client=clients["20111111111"],
            proposal=proposals["flujo_aprobacion"],
            document_type=Document.DocumentType.ANNEX,
            original_name="anexo_flujo_aprobacion.txt",
            filename="anexo_flujo_aprobacion.txt",
            content=(
                "Anexo demo para implementación de flujo de aprobación interno.\n"
            ),
            uploaded_by=users["advisor"],
        )

        self.upsert_document(
            client=clients["20456789012"],
            proposal=proposals["expedientes_historicos"],
            document_type=Document.DocumentType.REPORT,
            original_name="informe_expedientes_historicos.txt",
            filename="informe_expedientes_historicos.txt",
            content=(
                "Informe demo de reorganización de expedientes históricos.\n"
            ),
            uploaded_by=users["supervisor"],
        )

        self.upsert_document(
            client=clients["20601234567"],
            proposal=None,
            document_type=Document.DocumentType.BOND_LETTER,
            original_name="carta_fianza_techsolutions.txt",
            filename="carta_fianza_techsolutions.txt",
            content=(
                "Documento demo de carta fianza asociado al cliente TechSolutions.\n"
            ),
            uploaded_by=users["advisor"],
        )

    def upsert_document(
        self,
        *,
        client,
        proposal,
        document_type,
        original_name,
        filename,
        content,
        uploaded_by,
    ):
        document, created = Document.objects.get_or_create(
            client=client,
            proposal=proposal,
            document_type=document_type,
            original_name=original_name,
            defaults={"uploaded_by": uploaded_by},
        )

        if created or not document.file:
            document.uploaded_by = uploaded_by
            document.file.save(filename, ContentFile(content), save=True)