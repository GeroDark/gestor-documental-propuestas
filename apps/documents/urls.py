from django.urls import path

from .views import (
    DocumentCreateView,
    DocumentDetailView,
    DocumentDownloadView,
    DocumentListView,
)

urlpatterns = [
    path("", DocumentListView.as_view(), name="document-list"),
    path("new/", DocumentCreateView.as_view(), name="document-create"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("<int:pk>/download/", DocumentDownloadView.as_view(), name="document-download"),
]