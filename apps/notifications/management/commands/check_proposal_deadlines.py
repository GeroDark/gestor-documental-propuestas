from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.audit.services import log_audit
from apps.proposals.models import Proposal, ProposalStatusHistory

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Revisa propuestas por vencer o vencidas y, opcionalmente, "
        "marca como vencidas las atrasadas."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Cantidad de días hacia adelante para revisar propuestas por vencer.",
        )
        parser.add_argument(
            "--mark-expired",
            action="store_true",
            help="Marca como vencidas las propuestas atrasadas.",
        )
        parser.add_argument(
            "--changed-by",
            type=str,
            help="Username del usuario que registrará el cambio a vencida.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        mark_expired = options["mark_expired"]
        changed_by = options.get("changed_by")

        if days < 0:
            raise CommandError("--days no puede ser negativo.")

        acting_user = None
        if mark_expired:
            if not changed_by:
                raise CommandError(
                    "Debes indicar --changed-by <username> para marcar propuestas vencidas."
                )
            try:
                acting_user = User.objects.get(username=changed_by)
            except User.DoesNotExist as exc:
                raise CommandError(
                    f"No existe un usuario con username '{changed_by}'."
                ) from exc

        today = timezone.localdate()
        limit_date = today + timedelta(days=days)

        base_queryset = (
            Proposal.objects.select_related("client", "responsible", "created_by")
            .exclude(status__in=[Proposal.Status.APPROVED, Proposal.Status.REJECTED])
        )

        expiring_proposals = list(
            base_queryset.exclude(status=Proposal.Status.EXPIRED)
            .filter(due_date__range=(today, limit_date))
            .order_by("due_date", "id")
        )

        overdue_proposals = list(
            base_queryset.exclude(status=Proposal.Status.EXPIRED)
            .filter(due_date__lt=today)
            .order_by("due_date", "id")
        )

        self.stdout.write(self.style.NOTICE(f"Fecha actual: {today:%d/%m/%Y}"))
        self.stdout.write(
            self.style.NOTICE(
                f"Propuestas por vencer en los próximos {days} días: {len(expiring_proposals)}"
            )
        )

        if expiring_proposals:
            for proposal in expiring_proposals:
                self.stdout.write(
                    f"- [POR VENCER] ID={proposal.id} | "
                    f"Título={proposal.title} | "
                    f"Cliente={proposal.client.business_name} | "
                    f"Responsable={proposal.responsible.username} | "
                    f"Vence={proposal.due_date:%d/%m/%Y} | "
                    f"Estado={proposal.get_status_display()}"
                )
        else:
            self.stdout.write("No hay propuestas por vencer en ese rango.")

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                f"Propuestas vencidas pendientes de marcar: {len(overdue_proposals)}"
            )
        )

        if overdue_proposals:
            for proposal in overdue_proposals:
                self.stdout.write(
                    f"- [VENCIDA] ID={proposal.id} | "
                    f"Título={proposal.title} | "
                    f"Cliente={proposal.client.business_name} | "
                    f"Responsable={proposal.responsible.username} | "
                    f"Venció={proposal.due_date:%d/%m/%Y} | "
                    f"Estado actual={proposal.get_status_display()}"
                )
        else:
            self.stdout.write("No hay propuestas vencidas pendientes.")

        if mark_expired:
            updated = 0

            for proposal in overdue_proposals:
                previous_status = proposal.status
                proposal.status = Proposal.Status.EXPIRED
                proposal.save(update_fields=["status", "updated_at"])

                ProposalStatusHistory.objects.create(
                    proposal=proposal,
                    previous_status=previous_status,
                    new_status=Proposal.Status.EXPIRED,
                    comment="Marcada automáticamente como vencida mediante comando.",
                    changed_by=acting_user,
                )

                log_audit(
                    user=acting_user,
                    action="status_change",
                    instance=proposal,
                    description=(
                        f"La propuesta '{proposal.title}' cambió automáticamente "
                        f"de '{previous_status}' a '{Proposal.Status.EXPIRED}'."
                    ),
                )
                updated += 1

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Se marcaron {updated} propuesta(s) como vencida(s)."
                )
            )