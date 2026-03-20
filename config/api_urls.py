from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.clients.api_views import ClientViewSet
from apps.documents.api_views import DocumentViewSet
from apps.dashboard.api_views import DashboardSummaryAPIView
from apps.proposals.api_views import ProposalViewSet

router = DefaultRouter()
router.register(r"clients", ClientViewSet, basename="api-client")
router.register(r"proposals", ProposalViewSet, basename="api-proposal")
router.register(r"documents", DocumentViewSet, basename="api-document")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/summary/", DashboardSummaryAPIView.as_view(), name="api-dashboard-summary"),
]