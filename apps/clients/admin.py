from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "document_number",
        "email",
        "phone",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("business_name", "document_number", "email")
    ordering = ("-created_at",)