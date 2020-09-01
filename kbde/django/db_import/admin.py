from django.contrib import admin

from . import models


for model in [models.ImportFile,
              models.ImportColumn,
              models.ImportRow,
              models.ImportValue,
              models.ImportMapping,
              models.ImportMappingColumn,
              models.ImportMappingRow,
              models.Import,
              ]:
    admin.site.register(model)
