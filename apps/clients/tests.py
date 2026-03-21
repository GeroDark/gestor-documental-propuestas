from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.clients.models import Client

User = get_user_model()


class ClientExportCsvTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cliente_export_user",
            email="cliente_export@example.com",
            password="Test12345!",
        )
        self.user.user_permissions.add(Permission.objects.get(codename="view_client"))

        Client.objects.create(
            business_name="Cliente Activo SAC",
            document_number="20123456789",
            email="activo@example.com",
            phone="999111222",
            address="Lima",
            status=Client.Status.ACTIVE,
            created_by=self.user,
        )
        Client.objects.create(
            business_name="Cliente Inactivo SAC",
            document_number="20987654321",
            email="inactivo@example.com",
            phone="999333444",
            address="Huancayo",
            status=Client.Status.INACTIVE,
            created_by=self.user,
        )

    def test_export_clients_csv_respects_filters(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("client-export-csv"), {"status": Client.Status.ACTIVE})

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])

        content = response.content.decode("utf-8-sig")
        self.assertIn("Cliente Activo SAC", content)
        self.assertNotIn("Cliente Inactivo SAC", content)