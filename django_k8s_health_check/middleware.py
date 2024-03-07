from copy import copy

from django.conf import settings
from django.http import HttpRequest, HttpResponse
#from django.utils.deprecation import MiddlewareMixin

from django_k8s_health_check.settings import api_settings


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if self.validate_path(request):
            host = request._get_raw_host().split(':')[0]  # pylint: disable=protected-access

            if self.validate_host(request, host) and self.validate_origin(request, host):
                return HttpResponse(status=204)

        response: HttpResponse = self.get_response(request)

        return response

    ###
    # Validators
    ##
    def validate_path(self, request: HttpRequest):
        if api_settings.ALLOWED_PATHS is not None:
            return request.path in api_settings.ALLOWED_PATHS
        return True

    def validate_host(self, request: HttpRequest, host: str):  # pylint: disable=unused-argument
        if api_settings.ALLOWED_HOSTS is not None:
            return host in api_settings.ALLOWED_HOSTS
        return True

    def validate_origin(self, request: HttpRequest, host: str):  # pylint: disable=unused-argument
        return request.headers.get(api_settings.HEADER_FIELD) == api_settings.HEADER_VALUE
