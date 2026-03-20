from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.business_name", read_only=True)
    proposal_title = serializers.CharField(source="proposal.title", read_only=True)
    uploaded_by_username = serializers.CharField(source="uploaded_by.username", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "client",
            "client_name",
            "proposal",
            "proposal_title",
            "document_type",
            "file",
            "original_name",
            "uploaded_by",
            "uploaded_by_username",
            "uploaded_at",
        ]
        read_only_fields = ("original_name", "uploaded_by", "uploaded_at")