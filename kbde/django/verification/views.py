from django.conf import settings
from kbde.import_tools import utils as import_utils
from kbde.django import views as kbde_views

from . import models, forms


class VerificationCreate(kbde_views.CreateView):
    permission_classes = []

    @property
    def model(self):
        verification_class_name = self.kwargs["verification_class_name"]
        verification_class_path = (
            settings.ALLOWED_VERIFICATION_CLASSES.get(verification_class_name)
        )

        if verification_class_path is None:
            raise exceptions.SuspiciousOperation(
                f"The verification method {verification_class_name} is not "
                f"supported"
            )

        return import_utils.import_class_from_string(verification_class_path)
    
    @property
    def fields(self):
        self.model.get_form_fields()
        
    @property
    def template_name(self):
        self.model.get_template_name()


class VerificationVerify(kbde_views.UpdateView):
    model = models.Verification
    permission_classes = []
    form_class = forms.VerificationVerify
