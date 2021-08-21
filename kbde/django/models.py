from django import utils
from django.db import models
from django.core import exceptions
from django.contrib.auth import (models as auth_models,
                                 base_user,
                                 hashers)

from kbde.django import utils as kbde_utils

import random, datetime


MAX_LENGTH_CHAR_FIELD = 255


class User(auth_models.AbstractUser):

    class Meta:
        abstract = True


class EmailUserManager(base_user.BaseUserManager):

    def create_user(self, email, password=None):

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class EmailUser(User):
    email = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, unique=True)
    username = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)

    objects = EmailUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    class Meta:
        abstract = True

    def __str__(self):
        return self.email


class EmailVerificationMixin(models.Model):
    unverified_email = models.EmailField(blank=True)
    verification_code = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )
    verification_email_send_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        
        if self.unverified_email and not self.verification_email_send_time:
            self.request_email_verification()

        return result

    def request_email_verification(self):
        self.set_verification_code()
        self.send_verification_email()

    def set_verification_code(self):
        self.verification_code_raw = str(self.generate_verification_code())

        self.verification_code = hashers.make_password(
            self.verification_code_raw
        )

    def generate_verification_code(self):
        # TODO: make the number of digits configurable
        return int(random.random() * 10 ** 6)

    def send_verification_email(self):
        message = f"Your verification code is: {self.verification_code_raw}"

        kbde_utils.send_email(
            [self.unverified_email],
            "Your verification code",
            text_message=message,
        )

        self.verification_email_send_time = utils.timezone.now()
        self.save()
        
    def verify_email(self, verification_code):
        self.check_verification_code_expired()

        if not hashers.check_password(
            str(verification_code),
            self.verification_code,
        ):
            raise self.VerificationCodeIncorrect()

        # Verification passed

        self.email = self.unverified_email
        self.unverified_email = ""
        self.verification_code = ""
        self.verification_email_send_time = None

        self.save()

    def check_verification_code_expired(self):
        assert self.verification_email_send_time

        # TODO: make the expiration time configurable
        expire_time = (
              self.verification_email_send_time
            + datetime.timedelta(minutes=10)
        )
        if expire_time <= utils.timezone.now():
            self.verification_code = ""
            self.save()

            raise self.VerificationCodeExpired()

    class VerificationException(Exception):
        pass

    class VerificationCodeExpired(VerificationException):
        pass

    class VerificationCodeIncorrect(VerificationException):
        pass


class Schedule(models.Model):
    REPEAT_UNIT_DAY = 1
    REPEAT_UNIT_WEEK = 2
    REPEAT_UNIT_MONTH = 3
    REPEAT_UNIT_YEAR = 4
    REPEAT_UNIT_CHOICES = (
        (REPEAT_UNIT_DAY, "Day"),
        (REPEAT_UNIT_WEEK, "Week"),
        (REPEAT_UNIT_MONTH, "Month"),
        (REPEAT_UNIT_YEAR, "Year"),
        )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    # Repeat schedule
    repeat_frequency = models.IntegerField(default=1, blank=True)
    repeat_unit = models.IntegerField(choices=REPEAT_UNIT_CHOICES,
                                      null=True,
                                      blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.validate_fields()
        return super().save(*args, **kwargs)

    def validate_fields(self):
        # Make sure that the start date is before the end date
        if self.end_date is not None:
            if self.end_date < self.start_date:
                raise exceptions.ValidationError("End Date must be later than Start Date")

        # Make sure that the start time is before the end time
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise exceptions.ValidationError("End Time must be later than Start Time")

    def is_valid_now(self):
        """
        Checks to see if the time right now falls within this schedule
        """
        import dateutil

        now = utils.timezone.now()

        # Dates

        if self.start_date > now.date():
            raise self.BeforeStart

        if self.end_date is not None:
            if self.end_date < now.date():
                raise self.AfterEnd
        
        if self.end_date is None and self.repeat_unit is None:
            # This event has no end date and does not repeat
            # Treat the start date as the end date
            if self.start_date < now.date():
                raise self.AfterEnd

        # Repeated days

        since_start = now.date() - self.start_date

        if self.repeat_unit == self.REPEAT_UNIT_WEEK:
            # Need to calculate number of repeat days based on week frequency
            repeat_days = 7 * self.repeat_frequency
            # Check the mod of the days between events
            # If there is a remainder, then it's the wrong day
            if since_start.days % repeat_days:
                raise self.WrongDay

        if self.repeat_unit == self.REPEAT_UNIT_MONTH:
            # Check if the day is correct
            if now.date().day != self.start_date.day:
                raise self.WrongDay

            # Check to make sure that the proper number of months has elapsed
            month_delta = dateutil.relativedelta.relativedelta(now.date(), self.start_date)
            months_since_start = (month_delta.years * 12) + month_delta.months
            if months_since_start % self.repeat_frequency:
                raise self.WrongDay

        if self.repeat_unit == self.REPEAT_UNIT_YEAR:
            # Check if the day and month are correct
            if now.date().day != self.start_date.day:
                raise self.WrongDay
            if now.date().month != self.start_date.month:
                raise self.WrongDay

            # Check to make sure that the proper number of years has elapsed
            year_delta = dateutil.relativedelta.relativedelta(now.date(), self.start_date)
            years_since_start = year_delta.years
            if years_since_start % self.repeat_frequency:
                raise self.WrongDay

        # Time

        if self.start_time is not None:
            if self.start_time > now.time():
                raise self.BeforeStart

        if self.end_time is not None:
            if self.end_time <= now.time():
                raise self.AfterEnd

    class ScheduleException(Exception):
        pass

    class ScheduleValidException(ScheduleException):
        pass

    class BeforeStart(ScheduleValidException):
        pass

    class AfterEnd(ScheduleValidException):
        pass

    class WrongDay(ScheduleValidException):
        pass
