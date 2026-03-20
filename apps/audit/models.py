from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "Creación"
        UPDATE = "update", "Actualización"
        DELETE = "delete", "Eliminación"
        STATUS_CHANGE = "status_change", "Cambio de estado"
        COMMENT = "comment", "Comentario"
        LOGIN = "login", "Inicio de sesión"
        LOGOUT = "logout", "Cierre de sesión"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    model_name = models.CharField("entidad", max_length=100)
    object_id = models.CharField("ID del objeto", max_length=50, blank=True)
    description = models.TextField("descripción", blank=True)
    created_at = models.DateTimeField("fecha", auto_now_add=True)

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} - {self.created_at:%d/%m/%Y %H:%M}"