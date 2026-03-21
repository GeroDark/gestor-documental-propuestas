import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.clients.models import Client
from apps.documents.models import Document
from apps.proposals.models import Proposal

User = get_user_model()


class SeedDemoCommandTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media_dir = tempfile.mkdtemp()
        cls.override = override_settings(MEDIA_ROOT=cls.temp_media_dir)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls.temp_media_dir, ignore_errors=True)
        super().tearDownClass()

    def test_seed_demo_creates_expected_data_without_duplicates(self):
        call_command("seed_demo", reset=True)
        call_command("seed_demo")

        self.assertEqual(
            User.objects.filter(
                username__in=["admin_demo", "asesor_demo", "supervisor_demo"]
            ).count(),
            3,
        )
        self.assertEqual(
            Client.objects.filter(
                document_number__in=[
                    "20601234567",
                    "20567890123",
                    "20456789012",
                    "20111111111",
                ]
            ).count(),
            4,
        )
        self.assertEqual(
            Proposal.objects.filter(
                title__in=[
                    "Propuesta de digitalización documental 2026",
                    "Servicio de custodia documental - sede centro",
                    "Renovación de contrato marco de archivo",
                    "Implementación de flujo de aprobación interno",
                    "Propuesta de reorganización de expedientes históricos",
                    "Actualización de repositorio contractual 2025-2026",
                ]
            ).count(),
            6,
        )
        self.assertEqual(
            Document.objects.filter(
                original_name__in=[
                    "propuesta_digitalizacion_2026.txt",
                    "contrato_custodia_sede_centro.txt",
                    "renovacion_contrato_marco.txt",
                    "anexo_flujo_aprobacion.txt",
                    "informe_expedientes_historicos.txt",
                    "carta_fianza_techsolutions.txt",
                ]
            ).count(),
            6,
        )