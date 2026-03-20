from .models import AuditLog


def log_audit(*, user=None, action="", instance=None, description=""):
    AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        model_name=instance._meta.verbose_name if instance is not None else "",
        object_id=str(instance.pk) if instance is not None else "",
        description=description,
    )