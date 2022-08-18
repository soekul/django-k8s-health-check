from django.conf import settings
from django.core.cache import caches
from django.db import connections

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from django_k8s_health_check.settings import api_settings


class HealthView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        data, has_erro = self.mount_response_data()
        return Response(data, status=HTTP_500_INTERNAL_SERVER_ERROR if has_erro else HTTP_200_OK)

    def mount_response_data(self, request):
        data, has_error = {}, False
        
        if api_settings.SERVICE_NAME:
            data['data'] = api_settings.SERVICE_NAME
        
        if api_settings.CHECK_DATABASE:
            db_error, data['database'] = self.test_databases()
            has_error = has_error and db_error
        
        if api_settings.CHECK_CACHE:
            cache_error, data['cache'] = self.test_caches()
            has_error = has_error and cache_error
        
        return data, has_error
    
    ###
    # Helpers
    ##
    def test_databases(self):
        checks, has_error = {}, False
        for key in settings.DATABASES.keys():
            try:
                connections[key].cursor()
                checks[key] = True
            except Exception:
                checks[key] = False
                has_error = True
        
        return has_error, checks

    def test_caches(self):
        checks, has_error = {}, False
        for key in settings.DATABASES.keys():
            try:
                caches[key].get('invalid_key', None)
                checks[key] = True
            except Exception:
                checks[key] = False
                has_error = True
        
        return has_error, checks
