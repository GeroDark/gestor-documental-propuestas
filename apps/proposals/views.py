from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from .forms import ProposalCommentForm, ProposalForm, ProposalStatusForm
from .models import Comment, Proposal, ProposalStatusHistory


class ProposalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Proposal
    template_name = "proposals/proposal_list.html"
    context_object_name = "proposals"
    paginate_by = 10
    permission_required = "proposals.view_proposal"

    def get_queryset(self):
        queryset = Proposal.objects.select_related("client", "responsible", "created_by")

        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        responsible = self.request.GET.get("responsible", "").strip()
        due_from = self.request.GET.get("due_from", "").strip()
        due_to = self.request.GET.get("due_to", "").strip()

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(client__business_name__icontains=q) |
                Q(description__icontains=q)
            )

        if status:
            queryset = queryset.filter(status=status)

        if responsible:
            queryset = queryset.filter(responsible_id=responsible)

        if due_from:
            queryset = queryset.filter(due_date__gte=due_from)

        if due_to:
            queryset = queryset.filter(due_date__lte=due_to)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        from apps.accounts.models import User

        context = super().get_context_data(**kwargs)
        context["status_choices"] = Proposal.Status.choices
        context["responsible_users"] = User.objects.filter(is_active=True).order_by("username")
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "status": self.request.GET.get("status", ""),
            "responsible": self.request.GET.get("responsible", ""),
            "due_from": self.request.GET.get("due_from", ""),
            "due_to": self.request.GET.get("due_to", ""),
        }
        return context


class ProposalDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Proposal
    template_name = "proposals/proposal_detail.html"
    context_object_name = "proposal"
    permission_required = "proposals.view_proposal"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_form"] = ProposalStatusForm(user=self.request.user, proposal=self.object)
        context["comment_form"] = ProposalCommentForm()
        context["status_history"] = self.object.status_history.select_related("changed_by")
        context["comments"] = self.object.comments.select_related("user")
        return context


class ProposalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Proposal
    form_class = ProposalForm
    template_name = "proposals/proposal_form.html"
    permission_required = "proposals.add_proposal"
    success_url = reverse_lazy("proposal-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        ProposalStatusHistory.objects.create(
            proposal=self.object,
            previous_status="",
            new_status=self.object.status,
            comment="Creación inicial de la propuesta.",
            changed_by=self.request.user,
        )

        messages.success(self.request, "Propuesta creada correctamente.")
        return response


class ProposalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    template_name = "proposals/proposal_form.html"
    permission_required = "proposals.change_proposal"
    success_url = reverse_lazy("proposal-list")

    def form_valid(self, form):
        old_status = self.get_object().status
        response = super().form_valid(form)

        if old_status != self.object.status:
            ProposalStatusHistory.objects.create(
                proposal=self.object,
                previous_status=old_status,
                new_status=self.object.status,
                comment="Cambio de estado desde edición de propuesta.",
                changed_by=self.request.user,
            )

        messages.success(self.request, "Propuesta actualizada correctamente.")
        return response


class ProposalStatusUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = ProposalStatusForm
    permission_required = "proposals.change_proposal"

    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(Proposal, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["proposal"] = self.proposal
        return kwargs

    def form_valid(self, form):
        new_status = form.cleaned_data["status"]
        comment = form.cleaned_data["comment"]
        previous_status = self.proposal.status

        if new_status in {Proposal.Status.APPROVED, Proposal.Status.REJECTED}:
            is_allowed = (
                self.request.user.groups.filter(name="Administrador").exists()
                or self.request.user.groups.filter(name="Supervisor").exists()
            )
            if not is_allowed:
                messages.error(self.request, "No tienes permiso para aprobar o rechazar propuestas.")
                return HttpResponseRedirect(reverse("proposal-detail", args=[self.proposal.pk]))

        if previous_status != new_status:
            self.proposal.status = new_status
            self.proposal.save(update_fields=["status", "updated_at"])

            ProposalStatusHistory.objects.create(
                proposal=self.proposal,
                previous_status=previous_status,
                new_status=new_status,
                comment=comment,
                changed_by=self.request.user,
            )

            messages.success(self.request, "Estado actualizado correctamente.")
        else:
            messages.info(self.request, "La propuesta ya tenía ese estado.")

        return HttpResponseRedirect(reverse("proposal-detail", args=[self.proposal.pk]))


class ProposalCommentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Comment
    form_class = ProposalCommentForm
    permission_required = "proposals.change_proposal"

    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(Proposal, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.proposal = self.proposal
        form.instance.user = self.request.user
        messages.success(self.request, "Comentario agregado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("proposal-detail", args=[self.proposal.pk])