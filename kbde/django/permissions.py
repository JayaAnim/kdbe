from django import http
from django.contrib.auth import mixins as auth_mixins


class Permission:
    """
    Base class for a permission
    """

    def check(self, view):
        """
        Should either:
        
        - Return None (no problems)
        - Return a response object (to perform a redirect)
        - Raise a permission denied exception
        """
        raise NotImplementedError(
            f"{self.__class__} must implement .check()"
        )


class IsAuthenticated(Permission, auth_mixins.LoginRequiredMixin):
    
    def check(self, view):
        """
        Make sure that the current user is authenticated
        Returns a login redirect if not
        """
        if view.request.user and view.request.user.is_authenticated:
            return None
        
        # Path the request and let the LoginRequiredMixin handle the rest
        self.request = view.request
        return self.handle_no_permission()
