from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import FileResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from apps.audit.services import log_audit

from .forms import DocumentForm
from .models import Document


class DocumentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Document
    template_name = "documents/document_list.html"
    context_object_name = "documents"
    paginate_by = 10
    permission_required = "documents.view_document"

    def get_queryset(self):
        queryset = Document.objects.select_related(
            "client",
            "proposal",
            "uploaded_by",
        )

        q = self.request.GET.get("q", "").strip()
        document_type = self.request.GET.get("document_type", "").strip()

        if q:
            queryset = queryset.filter(
                Q(original_name__icontains=q)
                | Q(client__business_name__icontains=q)
                | Q(proposal__title__icontains=q)
            )

        if document_type:
            queryset = queryset.filter(document_type=document_type)

        return queryset.order_by("-uploaded_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["document_type_choices"] = Document.DocumentType.choices
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "document_type": self.request.GET.get("document_type", ""),
        }
        return context


class DocumentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Document
    template_name = "documents/document_detail.html"
    context_object_name = "document"
    permission_required = "documents.view_document"


class DocumentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = "documents/document_form.html"
    permission_required = "documents.add_document"
    success_url = reverse_lazy("document-list")

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        form.instance.original_name = form.cleaned_data["file"].name
        response = super().form_valid(form)

        log_audit(
            user=self.request.user,
            action="create",
            instance=self.object,
            description=f"Se subió el documento '{self.object.original_name}'.",
        )

        messages.success(self.request, "Documento subido correctamente.")
        return response


class DocumentDownloadView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Document
    permission_required = "documents.view_document"

    def get(self, request, *args, **kwargs):
        document = self.get_object()

        if not document.file:
            raise Http404("El archivo no existe.")

        return FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.original_name,
        )