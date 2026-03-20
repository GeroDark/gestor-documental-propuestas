from django.conf import settings
from django.db import models


class Client(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Activo"
        INACTIVE = "inactive", "Inactivo"

    business_name = models.CharField("razón social", max_length=255)
    document_number = models.CharField("RUC / identificación", max_length=20, unique=True)
    email = models.EmailField("correo electrónico")
    phone = models.CharField("teléfono", max_length=30, blank=True)
    address = models.CharField("dirección", max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField("observaciones", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="clients_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.business_name