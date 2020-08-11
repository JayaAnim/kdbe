from django.contrib import admin

from . import models


for model in [models.Report]:
    admin.site.register(model)
