from django.utils import functional

from . import models


class TokenAuthMiddleware:
    keyword = "Token"
    model = models.AuthToken
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = functional.SimpleLazyObject(lambda: self.get_user(request))
        return self.get_response(request)

    def get_user(self, request):
        if not hasattr(request, "_cached_user"):
            auth_token = self.get_auth_token(request)
            request._cached_user = auth_token.user

        return request._cached_user

    def get_auth_token(self, request):
        token_key = self.get_token_key(request)
        try:
            


    def get_token_key(self, request):
        auth_header = self.get_authorization_header(request)
        auth = auth_header.split()

        if not auth or auth[0].lower() != self.keyword.lower():
            return None

        if len(auth) < 1

    def get_authorization_header(self, request):
        return request.META.get("HTTP_AUTHORIZATION")
