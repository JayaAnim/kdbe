from kbde.django import views as kbde_views

from . import models, forms


class VerificationVerify(kbde_views.UpdateView):
    model = models.Verification
    permission_classes = []
    form_class = forms.VerificationVerify
