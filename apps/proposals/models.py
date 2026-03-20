from django.conf import settings
from django.db import models

from apps.clients.models import Client


class Proposal(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        SENT = "sent", "Enviada"
        IN_REVIEW = "in_review", "En revisión"
        APPROVED = "approved", "Aprobada"
        REJECTED = "rejected", "Rechazada"
        EXPIRED = "expired", "Vencida"

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="proposals")
    title = models.CharField("título", max_length=255)
    description = models.TextField("descripción", blank=True)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_proposals",
    )
    estimated_amount = models.DecimalField("monto estimado", max_digits=12, decimal_places=2)
    due_date = models.DateField("fecha límite")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="proposals_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "propuesta"
        verbose_name_plural = "propuestas"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title