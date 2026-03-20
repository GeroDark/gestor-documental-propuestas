from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"