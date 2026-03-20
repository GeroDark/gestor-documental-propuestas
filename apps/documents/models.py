from django.conf import settings
from django.db import models

from apps.clients.models import Client
from apps.proposals.models import Proposal


class Document(models.Model):
    class DocumentType(models.TextChoices):
        COMMERCIAL_PROPOSAL = "commercial_proposal", "Propuesta comercial"
        CONTRACT = "contract", "Contrato"
        BOND_LETTER = "bond_letter", "Carta fianza"
        REPORT = "report", "Informe"
        ANNEX = "annex", "Anexo"
        RECEIPT = "receipt", "Comprobante"

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file = models.FileField(upload_to="documents/")
    original_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_documents",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "documento"
        verbose_name_plural = "documentos"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_name