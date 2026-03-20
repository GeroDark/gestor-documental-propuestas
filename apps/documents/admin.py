from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "original_name",
        "document_type",
        "client",
        "proposal",
        "uploaded_by",
        "uploaded_at",
    )
    list_filter = ("document_type", "uploaded_at")
    search_fields = (
        "original_name",
        "client__business_name",
        "proposal__title",
        "uploaded_by__username",
    )
    ordering = ("-uploaded_at",)