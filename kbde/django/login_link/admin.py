from django.contrib import admin

from . import models


for model in [models.LoginLink]:
    admin.site.register(model)
