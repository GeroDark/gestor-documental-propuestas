from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "model_name", "object_id")
    list_filter = ("action", "model_name", "created_at")
    search_fields = ("description", "model_name", "object_id", "user__username", "user__email")
    ordering = ("-created_at",)