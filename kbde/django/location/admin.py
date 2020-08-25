from django.contrib import admin

from . import models


MODEL_LIST = [models.Location,
              models.Address,
              models.Point,
              ]

for model in MODEL_LIST:
    admin.site.register(model)
