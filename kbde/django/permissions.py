from django import http
from django.contrib.auth import mixins as auth_mixins
from django.contrib import messages


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


class RedirectWithNext(Permission):
    redirect_url = None
    redirect_message = None
    redirect_message_level = messages.INFO

    def check(self, view):
        if self.test_func(view):
            return None

        # Test function failed
        # Redirect with next param
        redirect_url = self.get_redirect_url(view)
        url = f"{redirect_url}?next={view.request.get_full_path()}"

        redirect_message = self.get_redirect_message(view)
        if redirect_message is not None:
            messages.add_message(
                view.request,
                self.get_redirect_message_level(view),
                redirect_message,
            )

        return http.HttpResponseRedirect(url)
        
    def test_func(self, view):
        raise NotImplementedError(
            f"{self.__class__} must implement .test_func(). "
            f"This function should return True or False"
        )
    
    def get_redirect_url(self, view):
        assert self.redirect_url is not None, (
            f"{self.__class__} must define .redirect_url or override "
            f".get_redirect_url()"
        )
        return self.redirect_url

    def get_redirect_message(self, view):
        return self.redirect_message

    def get_redirect_message_level(self, view):
        return self.redirect_message_level
