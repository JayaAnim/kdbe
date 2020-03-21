from django.core import management
from django.conf import settings

from user import models as user_models


class Command(management.base.BaseCommand):
    help = ("Gets or creates users for each email listed in the settings.ADMINS field. Makes them "
            "superusers and staff")

    def handle(self, *args, **options):
        for name, email in settings.ADMINS:
            # Get or create a user with the given email
            user, created = user_models.User.objects.get_or_create(email=email)

            user.is_superuser = True
            user.is_staff = True
            user.save()
