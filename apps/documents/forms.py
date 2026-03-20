from pathlib import Path

from django import forms

from apps.clients.models import Client
from apps.proposals.models import Proposal

from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "client",
            "proposal",
            "document_type",
            "file",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.order_by("business_name")
        self.fields["proposal"].queryset = Proposal.objects.select_related("client").order_by("-created_at")

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            return file

        allowed_extensions = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
        suffix = Path(file.name).suffix.lower()

        if suffix not in allowed_extensions:
            raise forms.ValidationError(
                "Solo se permiten archivos PDF, DOC, DOCX, XLS y XLSX."
            )

        return file

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        proposal = cleaned_data.get("proposal")

        if not client and not proposal:
            raise forms.ValidationError(
                "Debes asociar el documento a un cliente o a una propuesta."
            )

        return cleaned_data