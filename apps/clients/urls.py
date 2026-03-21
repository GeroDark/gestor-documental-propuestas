from django.urls import path

from .views import (
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientExportCsvView,
    ClientListView,
    ClientUpdateView,
)

urlpatterns = [
    path("", ClientListView.as_view(), name="client-list"),
    path("new/", ClientCreateView.as_view(), name="client-create"),
    path("export/csv/", ClientExportCsvView.as_view(), name="client-export-csv"),
    path("<int:pk>/", ClientDetailView.as_view(), name="client-detail"),
    path("<int:pk>/edit/", ClientUpdateView.as_view(), name="client-update"),
    path("<int:pk>/delete/", ClientDeleteView.as_view(), name="client-delete"),
]