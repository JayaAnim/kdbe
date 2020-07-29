from django.db import models
from django import forms
from django.core import exceptions
from polymorphic import models as poly_models

from ..models import MAX_LENGTH_CHAR_FIELD

import uuid


class FormGroup(models.Model):
    """
    A collection of forms
    """
    slug = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)

    def __str__(self):
        return self.title


class Form(models.Model):
    """
    The main collection of fields
    """
    form_group = models.ForeignKey(FormGroup, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    priority = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title or "Form {}".format(self.pk)
    
    def get_filled_forms(self):
        q = self.filledform_set.all()
        
        fields = self.get_fields()
        for field in fields:
            q = q.annotate(
                **{field.get_attr_name(): models.Subquery(
                    FieldValue.objects.filter(filled_form=models.OuterRef("pk"),
                                              field=field).values("value")
                    )}
                )

        return q

    def get_fields(self):
        return self.field_set.order_by("field_group__priority", "priority", "pk")


class FieldGroup(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    priority = models.IntegerField(null=True, blank=True)

    def clean(self):
        # Update all fields to have the same form as this group
        self.field_set.update(form=self.form)


class Field(poly_models.PolymorphicModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    field_group = models.ForeignKey(FieldGroup, on_delete=models.CASCADE, blank=True, null=True)
    priority = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)

    # Core field arguments
    required = models.BooleanField(default=True)
    label = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    label_suffix = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    initial = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    help_text = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    localize = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)

    exclude_field_names = [
        "fieldvalue",
        "id",
        "polymorphic_ctype",
        "field_ptr",
        "form",
        "field_group",
        "priority",
        "name",
        ]

    allowed_name_chars = "qwertyuiopasdfghjklzxcvbnm1234567890_"

    def __str__(self):
        return self.label or self.name or "Field {}".format(self.pk)

    def clean(self):
        # Same form as group
        if self.field_group and self.field_group.form != self.form:
            raise exceptions.ValidationError("Field group and this field must both have the same form")
        
        # Name characters
        name = self.name
        for char in self.allowed_name_chars:
            name = name.replace(char, "")
        if name:
            raise exceptions.ValidationError("Name must only contain lowercase letters, numbers, and dashes")

    def get_attr_name(self):
        return self.name or "field_{}".format(self.pk)

    def get_form_field(self):
        """
        returns a model field instance
        """
        form_field_class = self.get_form_field_class()
        form_field_kwargs = self.get_form_field_kwargs()
        return form_field_class(**form_field_kwargs)

    def get_form_field_kwargs(self):
        FieldClass = type(self)
        model_fields = FieldClass._meta.fields

        kwargs = {field.name: getattr(self, field.name) for field in model_fields
                    if field.name not in self.exclude_field_names}

        return kwargs

    def get_form_field_class(self):
        return self.form_field_class


class BooleanField(Field):
    form_field_class = forms.BooleanField


class CharField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)
    strip = models.BooleanField(default=True)
    empty_value = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)

    form_field_class = forms.CharField


class ChoiceField(Field):
    form_field_class = forms.ChoiceField

    def get_form_field_kwargs(self):
        kwargs = super().get_form_field_kwargs()

        kwargs["choices"] = self.get_choices()

        return kwargs

    def get_choices(self):
        return ((choice_model.value, choice_model.title) for choice_model in self.get_choice_models())
        
    def get_choice_models(self):
        return self.choice_set.order_by("priority", "id")


class Choice(models.Model):
    choice_field = models.ForeignKey(ChoiceField, on_delete=models.CASCADE)
    priority = models.IntegerField(null=True, blank=True)
    value = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD)
    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD)

    def __str__(self):
        return self.title


class DateField(Field):
    form_field_class = forms.DateField


class DateTimeField(Field):
    form_field_class = forms.DateTimeField


class DecimalField(Field):
    max_value = models.IntegerField(null=True, default=None, blank=True)
    min_value = models.IntegerField(null=True, default=None, blank=True)
    max_digits = models.IntegerField(null=True, default=None, blank=True)
    decimal_places = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.DecimalField


class DurationField(Field):
    form_field_class = forms.DurationField


class EmailField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.EmailField


class FileField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    allow_empty_file = models.BooleanField(default=False)

    form_field_class = forms.FileField


class FloatField(Field):
    max_value = models.IntegerField(null=True, default=None, blank=True)
    min_value = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.FloatField
    

class ImageField(Field):
    form_field_class = forms.ImageField


class IntegerField(Field):
    max_value = models.IntegerField(null=True, default=None, blank=True)
    min_value = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.IntegerField


class GenericIpAddressField(Field):
    PROTOCOL_BOTH = "both"
    PROTOCOL_IPV4 = "IPv4"
    PROTOCOL_IPV6 = "IPv6"
    PROTOCOL_CHOICES = (
        (PROTOCOL_BOTH, "Both"),
        (PROTOCOL_IPV4, PROTOCOL_IPV4),
        (PROTOCOL_IPV6, PROTOCOL_IPV6),
        )
    protocol = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, choices=PROTOCOL_CHOICES)
    unpack_ipv4 = models.BooleanField(default=False)

    form_field_class = forms.GenericIPAddressField


class MultipleChoiceField(ChoiceField):
    form_field_class = forms.MultipleChoiceField


class NullBooleanField(Field):
    form_field_class = forms.NullBooleanField


class RegexField(Field):
    regex = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)
    strip = models.BooleanField(default=False)

    form_field_class = forms.RegexField


class SlugField(Field):
    allow_unicode = models.BooleanField(default=False)

    form_field_class = forms.SlugField


class TimeField(Field):
    form_field_class = forms.TimeField


class UrlField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.URLField


class UuidField(Field):
    form_field_class = forms.UUIDField


class FilledForm(models.Model):
    slug = models.UUIDField(default=uuid.uuid4)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} - {}".format(self.form, self.time_created)

    def get_data(self):
        field_values = self.get_field_values()
        return {field_value.field.get_attr_name(): field_value.value for field_value in field_values}

    def get_field_values(self):
        return self.fieldvalue_set.order_by("field__priority", "field__pk").select_related("field")


class FieldValue(models.Model):
    filled_form = models.ForeignKey(FilledForm, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.TextField(blank=True)
