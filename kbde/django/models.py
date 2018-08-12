from django.contrib.auth.models import AbstractUser


MAX_LENGTH_CHAR_FIELD = 255


class User(AbstractUser):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)
