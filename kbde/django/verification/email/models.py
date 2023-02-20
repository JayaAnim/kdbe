from django.db import models
from django.conf import settings
from django.template import loader
from kbde.django import (
    models as kbde_models,
    utils as kbde_utils,
)

from ..models import base


class EmailVerification(base.Verification):
    email = models.EmailField()
    subject = models.CharField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        default=getattr(
            settings,
            "VERIFICATION_EMAIL_DEFAULT_SUBJECT",
            "Verification Code"
        ),
    )
    from_email = models.EmailField(blank=True)
    email_template_name = getattr(
        settings,
        "VERIFICATION_EMAIL_TEMPLATE_NAME",
        "kbde/django/verification/email/verification_email.html",
    )

    def send(self, raw_key):
        email_context = {
            "object": self,
            "raw_key": raw_key,
        }
        email_template_name = self.get_email_template_name()
        email_html = loader.render_to_string(
            email_template_name,
            email_context,
        )

        kbde_utils.send_email(
            [self.email],
            subject=self.subject,
            html_message=email_html,
            from_email=self.from_email or None,
        )

    def get_email_template_name(self):
        return self.email_template_name
