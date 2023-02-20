from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import hashers
from kbde.django import models as kbde_models

from polymorphic import models as poly_models

import uuid, random, datetime


class Verification(poly_models.PolymorphicModel):
    slug = models.UUIDField(default=uuid.uuid4)

    key_allowed_characters = "0123456789ABCDEF"
    key_length = models.PositiveIntegerField(default=6)
    key = models.CharField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )

    time_created = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    time_sent = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    time_completed = models.DateTimeField(null=True, blank=True)

    time_valid = models.PositiveIntegerField(
        blank=True,
        default=getattr(
            settings,
            "VERIFICATION_DEFAULT_TIME_VALID",
            10 * 60,  # 10 minutes
        )
    )
    expire_time = models.DateTimeField(null=True, blank=True)

    template_name = "kbde/django/verification/views/VerificationCreate.html"
    form_fields = None

    @classmethod
    def get_template_name(cls):
        return cls.template_name

    @classmethod
    def get_form_fields(cls):
        assert cls.form_fields is not None, (
            f"{cls} must define .form_fields"
        )

    def save(self, *args, **kwargs):

        if self.expire_time is None and self.time_valid is not None:
            self.expire_time = (
                timezone.now() + datetime.timedelta(seconds=self.time_valid)
            )

        raw_key = None

        if not self.key:
            raw_key = self.generate_key()
            self.key = hashers.make_password(raw_key)

        if raw_key and not self.is_sent:
            self.is_completed = False
            self.send(raw_key)
            self.is_sent = True
            self.time_sent = timezone.now()

        if self.is_completed:
            self.time_completed = self.time_completed or timezone.now()
        else:
            self.time_completed = None

        return super().save(*args, **kwargs)
        
    def generate_key(self):
        """
        By default, this just returns a random string made of characters found
        in self.key_allowed_characters, and a length of self.key_length
        """
        return "".join(
            random.choice(self.key_allowed_characters).upper()
            for i in range(self.key_length)
        )

    def send(self, raw_key):
        """
        Send the raw key so the user can verify that they received it
        """
        raise NotImplementedError(
            f"{self.__class__} must implement .send()"
        )

    def verify(self, raw_key):

        if self.expire_time is not None and self.expire_time <= timezone.now():
            raise self.VerificationExpired

        if not hashers.check_password(raw_key.upper(), self.key):
            raise self.IncorrectKey

        self.is_completed = True
        self.save()

    def get_time_valid_minutes(self):

        if self.time_valid is None:
            return None

        return int(self.time_valid / 60)

    class VerificationException(Exception):
        pass

    class VerificationFailed(VerificationException):
        pass

    class VerificationExpired(VerificationFailed):
        pass

    class IncorrectKey(VerificationFailed):
        pass
