from django.contrib import admin

from . import models


for model in [models.ImportFile,
              models.ImportMapping,
              models.ImportMappingColumn]:
    admin.site.register(model)
