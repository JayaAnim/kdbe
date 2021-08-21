from django import urls
from kbde.django import views as kbde_views

from . import forms, models


class LoginLinkCreate(kbde_views.CreateView):
    form_class = forms.LoginLinkCreate
    prompt_text = "Login"
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
    prompt_text = "Please access the login code to proceed"
    permission_classes = []

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
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
    prompt_text = "Please confirm login attempt"
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
