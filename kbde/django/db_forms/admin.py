from django.contrib import admin

from . import models


MODEL_LIST = [models.Form,
              models.BooleanField,
              models.CharField,
              models.ChoiceField,
              models.Choice,
              models.DateField,
              models.DateTimeField,
              models.DecimalField,
              models.DurationField,
              models.EmailField,
              models.FileField,
              models.FloatField,
              models.ImageField,
              models.IntegerField,
              models.GenericIpAddressField,
              models.MultipleChoiceField,
              models.NullBooleanField,
              models.RegexField,
              models.SlugField,
              models.TimeField,
              models.UuidField,
              models.FilledForm,
              ]

for model in MODEL_LIST:
    admin.site.register(model)
