from django.contrib import admin

from . import models


for model in [models.ImportFile]:
    admin.site.register(model)
