from django.conf import settings
from django.utils import functional, crypto
from django.contrib import auth
from django.contrib.auth import models as auth_models

import importlib


class SessionHeaderAuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

        engine = importlib.import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def __call__(self, request):
        request.session_header_user = functional.SimpleLazyObject(
            lambda: self.get_session_header_user(request)
        )
        return self.get_response(request)

    def get_session_header_user(self, request):
        if not hasattr(request, "_cached_session_header_user"):
            request._cached_session_header_user = self.get_user_from_request(request)
        
        return request._cached_session_header_user

    def get_user_from_request(self, request):
        session = self.get_session_from_request(request)

        if session is None:
            return auth_models.AnonymousUser()

        try:
            user_id = auth.get_user_model()._meta.pk.to_python(session[auth.SESSION_KEY])
            backend_path = session[auth.BACKEND_SESSION_KEY]
        except KeyError:
            return auth_models.AnonymousUser()

        if backend_path not in settings.AUTHENTICATION_BACKENDS:
            return auth_models.AnonymousUser()

        backend = auth.load_backend(backend_path)
        user = backend.get_user(user_id)

        # Verify the session
        if not hasattr(user, 'get_session_auth_hash'):
            return auth_models.AnonymousUser()

        session_hash = session.get(auth.HASH_SESSION_KEY)
        session_hash_verified = (
            session_hash
            and crypto.constant_time_compare(
                session_hash,
                user.get_session_auth_hash()
            )
        )
        if not session_hash_verified:
            session.flush()
            return auth_models.AnonymousUser()

        return user

    def get_session_from_request(self, request):
        session_key = self.get_session_key_from_request(request)

        if session_key is None:
            return None

        return self.SessionStore(session_key)

    def get_session_key_from_request(self, request):
        auth_header = request.headers.get("authorization")
        
        if not auth_header:
            return None

        auth = auth_header.split()

        if auth[0].lower() != settings.SESSION_COOKIE_NAME.lower():
            return None

        if len(auth) != 2:
            return None

        return auth[1]
