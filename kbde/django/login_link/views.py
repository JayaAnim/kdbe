from django import urls
from kbde.django import views as kbde_views

from . import forms, models


class LoginLinkCreate(kbde_views.CreateView):
    form_class = forms.LoginLinkCreate
    login_link_url_name = "login_link:LoginLinkAuthenticate"
    permission_classes = []

    def get_success_url(self):
        return urls.reverse(
            self.login_link_url_name,
            args=[self.object.slug],
        )


class LoginLinkAuthenticate(kbde_views.UpdateView):
    template_name = "kbde_login_link/LoginLinkAuthenticate.html"
    model = models.LoginLink
    form_class = forms.LoginLinkAuthenticate
    confirm_text = "Please access the login link to proceed."
    check_auth_milliseconds = 3000
    permission_classes = []

    def get_check_auth_milliseconds(self):
        return self.check_auth_milliseconds

    def get_confirm_text(self):
        return self.confirm_text

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["confirm_text"] = self.get_confirm_text()
        return kwargs

    def get_success_url(self):
        return "/"


class LoginLinkConfirm(kbde_views.UpdateView):
    template_name = "kbde_login_link/LoginLinkConfirm.html"
    model = models.LoginLink
    slug_url_kwarg = "secret"
    slug_field = "secret"
    fields = [
        "confirmed",
    ]
    login_link_confirm_url_name = "login_link:LoginLinkConfirmResult"
    permission_classes = []

    def get_success_url(self):
        return urls.reverse(
            self.login_link_confirm_url_name,
            args=[self.object.slug],
        )


class LoginLinkConfirmResult(kbde_views.DetailView):
    template_name = "kbde_login_link/LoginLinkConfirmResult.html"
    model = models.LoginLink
    permission_classes = []
