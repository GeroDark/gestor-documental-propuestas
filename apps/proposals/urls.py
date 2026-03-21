from django.urls import path

from .views import (
    ProposalCommentCreateView,
    ProposalCreateView,
    ProposalDetailView,
    ProposalExportCsvView,
    ProposalListView,
    ProposalStatusUpdateView,
    ProposalUpdateView,
)

urlpatterns = [
    path("", ProposalListView.as_view(), name="proposal-list"),
    path("new/", ProposalCreateView.as_view(), name="proposal-create"),
    path("export/csv/", ProposalExportCsvView.as_view(), name="proposal-export-csv"),
    path("<int:pk>/", ProposalDetailView.as_view(), name="proposal-detail"),
    path("<int:pk>/edit/", ProposalUpdateView.as_view(), name="proposal-update"),
    path("<int:pk>/change-status/", ProposalStatusUpdateView.as_view(), name="proposal-change-status"),
    path("<int:pk>/comments/new/", ProposalCommentCreateView.as_view(), name="proposal-comment-create"),
]