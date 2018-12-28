from django.contrib.auth.models import AbstractUser


MAX_LENGTH_CHAR_FIELD = 255


class User(AbstractUser):
    username_is_email = True

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.username_is_email:
            self.username = self.email
        super().save(*args, **kwargs)
