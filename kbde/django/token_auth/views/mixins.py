

class TokenUserMixin:

    def setup(self, request, *args, **kwargs):
        """
        Override the request's `user` attribute with the value of the
        `token_user` attribute. This prevents actions from being performed
        based on session authentication.

        If there is no `token_user` attribute on the request, this means that
        `kbde.django.token_auth.middleware.TokenAuthMiddleware class is not 
        in use. This function will complain if that is the case.
        """
        assert hasattr(request, "token_user"), (
            "It looks like the "
            "`kbde.django.token_auth.middleware.TokenAuthMiddleware` "
            "is not installed"
        )

        request.user = request.token_user
            
        return super().setup(request, *args, **kwargs)
