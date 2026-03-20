from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.audit.services import log_audit

from .forms import ClientForm
from .models import Client


class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"
    paginate_by = 10
    permission_required = "clients.view_client"

    def get_queryset(self):
        queryset = Client.objects.select_related("created_by").all()

        q = self.request.GET.get("q", "").strip()
        document_number = self.request.GET.get("document_number", "").strip()
        status = self.request.GET.get("status", "").strip()
        created_from = self.request.GET.get("created_from", "").strip()
        created_to = self.request.GET.get("created_to", "").strip()

        if q:
            queryset = queryset.filter(
                Q(business_name__icontains=q) |
                Q(email__icontains=q)
            )

        if document_number:
            queryset = queryset.filter(document_number__icontains=document_number)

        if status:
            queryset = queryset.filter(status=status)

        if created_from:
            queryset = queryset.filter(created_at__date__gte=created_from)

        if created_to:
            queryset = queryset.filter(created_at__date__lte=created_to)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Client.Status.choices
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "document_number": self.request.GET.get("document_number", ""),
            "status": self.request.GET.get("status", ""),
            "created_from": self.request.GET.get("created_from", ""),
            "created_to": self.request.GET.get("created_to", ""),
        }
        return context


class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Client
    template_name = "clients/client_detail.html"
    context_object_name = "client"
    permission_required = "clients.view_client"


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    permission_required = "clients.add_client"
    success_url = reverse_lazy("client-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        log_audit(
            user=self.request.user,
            action="create",
            instance=self.object,
            description=f"Se creó el cliente '{self.object.business_name}'.",
        )

        messages.success(self.request, "Cliente creado correctamente.")
        return response


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    permission_required = "clients.change_client"
    success_url = reverse_lazy("client-list")

    def form_valid(self, form):
        response = super().form_valid(form)

        log_audit(
            user=self.request.user,
            action="update",
            instance=self.object,
            description=f"Se actualizó el cliente '{self.object.business_name}'.",
        )

        messages.success(self.request, "Cliente actualizado correctamente.")
        return response


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    template_name = "clients/client_confirm_delete.html"
    context_object_name = "client"
    permission_required = "clients.delete_client"
    success_url = reverse_lazy("client-list")

    def form_valid(self, form):
        client = self.get_object()

        log_audit(
            user=self.request.user,
            action="delete",
            instance=client,
            description=f"Se eliminó el cliente '{client.business_name}'.",
        )

        messages.success(self.request, "Cliente eliminado correctamente.")
        return super().form_valid(form)