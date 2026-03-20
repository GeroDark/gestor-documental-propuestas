from django import forms

from apps.accounts.models import User
from apps.clients.models import Client

from .models import Comment, Proposal


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = [
            "client",
            "title",
            "description",
            "responsible",
            "estimated_amount",
            "due_date",
            "status",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.order_by("business_name")
        self.fields["responsible"].queryset = User.objects.filter(is_active=True).order_by("username")


class ProposalStatusForm(forms.Form):
    status = forms.ChoiceField(label="Nuevo estado")
    comment = forms.CharField(
        label="Comentario",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, user=None, proposal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.proposal = proposal

        restricted_statuses = {
            Proposal.Status.APPROVED,
            Proposal.Status.REJECTED,
            Proposal.Status.EXPIRED,
        }

        if user and (user.groups.filter(name="Administrador").exists() or user.groups.filter(name="Supervisor").exists()):
            choices = [
                (value, label)
                for value, label in Proposal.Status.choices
                if value != Proposal.Status.EXPIRED
            ]
        else:
            choices = [
                (value, label)
                for value, label in Proposal.Status.choices
                if value not in restricted_statuses
            ]

        self.fields["status"].choices = choices


class ProposalCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Escribe un comentario interno..."})
        }