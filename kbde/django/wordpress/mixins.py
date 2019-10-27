from django.contrib.auth import (mixins as auth_mixins,
                                 views as auth_views)

from . import models


class WordpressAccess(auth_mixins.AccessMixin):
    
    def get_login_url(self):
        login_url = self.login_url or models.WpOptions.get_login_url()

        assert login_url, "Could not get login_url from this class, or from wordpress options"

        return str(login_url)

    def handle_no_permission(self):
        if self.raise_exception:
            raise exceptions.PermissionDenied(self.get_permission_denied_message())

        return auth_views.redirect_to_login(self.request.get_full_path(),
                                            self.get_login_url(),
                                            self.get_redirect_field_name())


class LoginRequired(WordpressAccess):
    
    def dispatch(self, request, *args, **kwargs):
        if not self.request.wordpress_user:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class UserPassesTest(WordpressAccess, auth_mixins.UserPassesTestMixin):
    pass
