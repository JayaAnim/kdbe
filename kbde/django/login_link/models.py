from django import utils
from django.core import exceptions
from django.db import models
from django.conf import settings

import uuid, datetime


class LoginLink(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    secret = models.UUIDField(default=uuid.uuid4, editable=False)
    time_created = models.DateTimeField(auto_now_add=True, editable=False)
    expire_time = models.DateTimeField(blank=True, editable=False)
    confirmed = models.BooleanField(null=True)

    # Amount of time, in mintues, which a LoginLink will be valid
    time_valid = getattr(settings, "LOGIN_LINK_TIME_VALID", 10)

    expired_error = "This login link is expired"

    @classmethod
    def get_user_read_queryset(cls, user):
        return cls.objects.all()

    @classmethod
    def get_user_update_queryset(cls, user):
        return cls.objects.all()

    def clean(self):
        if self.confirmed is not None and self.get_is_expired():
            raise exceptions.ValidationError(self.expired_error)

        if self.pk:
            instance = self.__class__.objects.get(pk=self.pk)
            if (
                instance.confirmed is not None and
                self.confirmed != instance.confirmed
            ):
                raise exceptions.ValidationError("Login link is no longer valid")

    def save(self, *args, **kwargs):
        self.expire_time = self.expire_time or (
            utils.timezone.now()
            + datetime.timedelta(minutes=self.time_valid)
        )
        created = not bool(self.pk)

        result = super().save(*args, **kwargs)

        if created:
            self.user.send_login_link(self)

        return result

    def get_is_expired(self):
        return utils.timezone.now() >= self.expire_time
