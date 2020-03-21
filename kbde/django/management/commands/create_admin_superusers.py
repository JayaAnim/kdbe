from django.core import management
from django.conf import settings
from django.contrib import auth


class Command(management.base.BaseCommand):
    help = ("Gets or creates users for each email listed in the settings.ADMINS field. Makes them "
            "superusers and staff")

    def handle(self, *args, **options):
        User = auth.get_user_model()

        for name, email in settings.ADMINS:
            # Get or create a user with the given email
            user_fields = {User.USERNAME_FIELD: email}

            user, created = User.objects.get_or_create(**user_fields)

            user.is_superuser = True
            user.is_staff = True
            user.save()
