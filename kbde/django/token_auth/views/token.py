from django.contrib.auth import forms as auth_forms
from kbde.django.json_views import views as json_views

from .. import models


class AuthTokenDetail(json_views.DetailView):
    model = models.AuthToken
    fields = [
        "user_id",
        "key",
        "time_created",
        "expire_time",
    ]


class AuthTokenCreate(json_views.ModelFormMixin, json_views.FormView):
    form_class = auth_forms.AuthenticationForm
    auth_token_model = models.AuthToken
    permission_classes = []
    detail_view_class = AuthTokenDetail

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.auth_token = None

    def form_valid(self, form):
        self.object, created = self.get_or_create_auth_token(
            form.get_user(),
        )
        return super().form_valid(form)

    def get_or_create_auth_token(self, user):
        return self.auth_token_model.objects.get_or_create(
            user=user,
        )
