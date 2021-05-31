from django.utils import functional
from django.contrib.auth import models as auth_models

from . import models


class TokenAuthMiddleware:
    keyword = "Token"
    model = models.AuthToken
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.token_user = functional.SimpleLazyObject(
            lambda: self.get_token_user(request)
        )

        return self.get_response(request)

    def get_token_user(self, request):
        if not hasattr(request, "_cached_token_user"):
            auth_token = self.get_auth_token(request)
            if auth_token is None:
                user = auth_models.AnonymousUser()
            else:
                user = auth_token.user

            request._cached_token_user = user

        return request._cached_token_user

    def get_auth_token(self, request):
        token_key = self.get_token_key(request)
        try:
            token = self.model.objects.get(key=token_key)
        except self.model.DoesNotExist:
            return None

        if not token.get_is_valid():
            return None

        if not token.user.is_active:
            return None

        return token

    def get_token_key(self, request):
        auth_header = self.get_authorization_header(request)
        auth = auth_header.split()

        if not auth or auth[0].lower() != self.keyword.lower():
            return None

        if len(auth) != 2:
            return None

        return auth[1]

    def get_authorization_header(self, request):
        return request.META.get("HTTP_AUTHORIZATION", "")
