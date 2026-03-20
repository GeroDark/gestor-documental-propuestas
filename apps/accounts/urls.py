from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import ProfileView

urlpatterns = [
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
