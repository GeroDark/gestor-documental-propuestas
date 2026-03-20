from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import UserProfileForm
from .models import User


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user