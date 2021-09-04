from django import utils
from django.db import models
from django.conf import settings

import datetime, uuid


class AuthToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    key = models.UUIDField(default=uuid.uuid4)
    time_created = models.DateTimeField(default=utils.timezone.now)
    expire_time = models.DateTimeField(null=True, blank=True)

    # Amount of time, in seconds, which an AuthToken will be valid
    time_valid = getattr(
        settings,
        "AUTH_TOKEN_TIME_VALID",
        settings.SESSION_COOKIE_AGE,
    )

    def save(self, *args, **kwargs):
        if not self.pk and self.expire_time is None:
            self.set_expire_time()

        return super().save(*args, **kwargs)

    def set_expire_time(self):
        """
        Sets the expire_time for this token if the AUTH_TOKEN_TIME_VALID
        setting is set. Otherwise sets the expire_time to `None`
        """
        if self.time_valid is None:
            self.expire_time = None
        else:
            assert isinstance(self.time_valid, int), (
                f"`time_valid` must be an int. Got type(self.time_valid) "
                f"instead"
            )

            self.expire_time = (
                self.time_created + datetime.timedelta(seconds=self.time_valid)
            )

    def get_is_valid(self):
        return (
            self.expire_time is None
            or self.expire_time > utils.timezone.now()
        )
