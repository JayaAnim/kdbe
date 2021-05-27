from django import utils
from django.db import models
from django.conf import settings

import datetime


class AuthToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    key = models.UUIDField(default=uuid.uuid4)
    time_created = models.DateTimeField(auto_now_add=True)

    # Amount of time, in mintues, which an AuthToken will be valid
    time_valid = getattr(settings, "AUTH_TOKEN_TIME_VALID", None)

    def get_is_valid(self):
        if time_valid is None:
            return True

        expire_time = (
            self.time_created + datetime.timedelta(minutes=self.time_valid)
        )

        return utils.timezone.now() < expire_time
