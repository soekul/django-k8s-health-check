from django.conf import settings
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from django_k8s_health_check.settings import api_settings


class HealthCheckMiddleware(MiddlewareMixin):
    header_field = api_settings.HEADER_FIELD

    def process_request(self, request: HttpRequest):
        if self.validate_path(self, request):
            host = request._get_raw_host()

            if self.validate_host(request, host) and self.validate_origin(request, host):
                if host not in settings.ALLOWED_HOSTS:
                    setattr(self, 'OLD_ALLOWED_HOSTS', settings.ALLOWED_HOSTS)
                    settings.ALLOWED_HOSTS += [host]

    def process_response(self, request: HttpRequest):
        if hasattr(self, 'OLD_ALLOWED_HOSTS'):
            settings.ALLOWED_HOSTS = self.OLD_ALLOWED_HOSTS

    ###
    # Validators
    ##
    def validate_path(self, request: HttpRequest):
        if api_settings.ALLOWED_PATHS is not None:
            return request.path in api_settings.ALLOWED_PATHS
        return True

    def validate_host(self, request: HttpRequest, host: str):
        if api_settings.ALLOWED_HOSTS is not None:
            return request.path in api_settings.ALLOWED_HOSTS
        return True
    
    def validate_origin(self, request: HttpRequest, host: str):
        return request.headers.get(self.header_field) == api_settings.HEADER_VALUE
