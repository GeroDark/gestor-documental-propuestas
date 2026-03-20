from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "business_name",
            "document_number",
            "email",
            "phone",
            "address",
            "status",
            "notes",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_by", "created_at", "updated_at")