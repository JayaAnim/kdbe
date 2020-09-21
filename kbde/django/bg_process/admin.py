from django.contrib import admin

from . import models


for model in [models.BgProcessModel]:
    admin.site.register(model)
