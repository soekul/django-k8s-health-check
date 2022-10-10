from django.core.management.base import BaseCommand

from django_k8s_health_check.settings import api_settings
from django_k8s_health_check.utils import HealthCheck


class Command(BaseCommand):
    help = 'Check databases and caches connection'

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        if api_settings.CHECK_DATABASE:
            db_error, _ = HealthCheck.test_databases()
            if db_error:
                raise Exception('Database connection error')

        if api_settings.CHECK_CACHE:
            cache_error, _ = HealthCheck.test_caches()
            if cache_error:
                raise Exception('Cache connection error')

        self.stdout.write('Databases and caches ok')
