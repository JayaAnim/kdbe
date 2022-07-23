from django import forms, utils
from django.db import models
from django.core import exceptions
from polymorphic import models as poly_models

from ..models import MAX_LENGTH_CHAR_FIELD

import uuid


class Form(models.Model):
    """
    The main collection of fields
    """
    slug = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)

    def __str__(self):
        return self.title or f"Form {self.pk}"
    
    def get_filled_forms(self):
        q = self.filledform_set.all()
        
        fields = self.get_fields()

        for field in fields:
            q = q.annotate(
                **{field.get_attr_name(): (
                    models.Subquery(
                        FieldValue.objects
                        .filter(
                            filled_form=models.OuterRef("pk"),
                            field=field,
                        )
                        .values("value")
                    )
                )}
            )

        return q

    def get_fields(self):
        return self.field_set.order_by("field_group__priority", "priority")


class FieldGroup(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    priority = models.IntegerField()

    class Meta:
        unique_together = ("form", "priority")

    def clean(self):
        super().clean()

        # Make sure that all fields moved to a new form are clean
        for field in self.get_fields():
            field.form = self.form
            field.clean()

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)

        self.get_fields.update(form=self.form)

        return result

    def get_fields(self):
        return self.field_set.order_by("priority")


class Field(poly_models.PolymorphicModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, blank=True)
    field_group = models.ForeignKey(
        FieldGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    priority = models.IntegerField()
    name = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        blank=True,
        null=True,
    )

    # Core field arguments
    required = models.BooleanField(default=True)
    label = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    label_suffix = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )
    initial = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    help_text = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    localize = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)

    form_field_names = [
        "required",
        "label",
        "label_suffix",
        "initial",
        "help_text",
        "localize",
        "disabled",
    ]
    extra_form_field_names = None

    ALLOWED_NAME_CHARS = "qwertyuiopasdfghjklzxcvbnm1234567890_"

    class Meta:
        unique_together = (
            ("form", "name"),
            ("form", "priority"),
        )

    def __str__(self):
        return self.label or self.name or "Field {}".format(self.pk)

    def clean(self):
        if self.name:
            # Name characters
            if set(self.name) - set(self.ALLOWED_NAME_CHARS):
                raise exceptions.ValidationError(
                    "Name must only contain lowercase letters, numbers, and "
                    "underscores"
                )

            if (
                self.__class__.objects
                .exclude(pk=self.pk)
                .filter(form=self.form, name=self.name)
                .exists()
            ):
                raise exceptions.ValidationError({
                    "name": (
                        f"A field with the name {self.name} already exists on "
                        f"form {self.form}"
                    ),
                })

    def save(self, *args, **kwargs):
        field_group = getattr(self, "field_group", None)

        if field_group is not None:
            self.form = field_group.form

        return super().save(*args, **kwargs)

    def get_attr_name(self):
        return self.name or f"field_{self.pk}"

    def get_form_field(self):
        """
        returns a model field instance
        """
        form_field_class = self.get_form_field_class()
        form_field_kwargs = self.get_form_field_kwargs()
        return form_field_class(**form_field_kwargs)

    def get_form_field_kwargs(self):
        kwargs = {
            field_name: getattr(self, field_name)
            for field_name in self.get_form_field_names()
        }

        return kwargs

    def get_form_field_names(self):
        assert self.extra_form_field_names is not None, (
            f"{self.__class__} must define .extra_form_field_names, an "
            f"iterable of field names that must be passed to construct "
            f"a form field from this type of instance"
        )

        return self.form_field_names + self.extra_form_field_names

    def get_form_field_class(self):
        return self.form_field_class


class BooleanField(Field):
    form_field_class = forms.BooleanField
    extra_form_field_names = []


class CharField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)
    strip = models.BooleanField(default=True)
    empty_value = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )

    form_field_class = forms.CharField
    extra_form_field_names = [
        "max_length",
        "min_length",
        "strip",
        "empty_value",
    ]


class ChoiceField(Field):
    form_field_class = forms.ChoiceField
    extra_form_field_names = []

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
    priority = models.IntegerField()
    value = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD)
    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD)

    def __str__(self):
        return self.title


class DateField(Field):
    form_field_class = forms.DateField
    extra_form_field_names = []


class DateTimeField(Field):
    form_field_class = forms.DateTimeField
    extra_form_field_names = []


class DecimalField(Field):
    max_value = models.IntegerField(null=True, default=None, blank=True)
    min_value = models.IntegerField(null=True, default=None, blank=True)
    max_digits = models.IntegerField(null=True, default=None, blank=True)
    decimal_places = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.DecimalField
    extra_form_field_names = [
        "max_value",
        "min_value",
        "max_digits",
        "decimal_places",
    ]


class DurationField(Field):
    form_field_class = forms.DurationField
    extra_form_field_names = []


class EmailField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.EmailField
    extra_form_field_names = [
        "min_length",
        "max_length",
    ]


class FileField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    allow_empty_file = models.BooleanField(default=False)

    form_field_class = forms.FileField
    extra_form_field_names = [
        "max_length",
        "allow_empty_file",
    ]


class FloatField(Field):
    max_value = models.IntegerField(null=True, default=None, blank=True)
    min_value = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.FloatField
    extra_form_field_names = [
        "min_value",
        "max_value",
    ]
    

class ImageField(Field):
    form_field_class = forms.ImageField
    extra_form_field_names = []


class IntegerField(Field):
    max_value = models.IntegerField(null=True, default=None, blank=True)
    min_value = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.IntegerField
    extra_form_field_names = [
        "min_value",
        "max_value",
    ]


class GenericIpAddressField(Field):
    PROTOCOL_BOTH = "both"
    PROTOCOL_IPV4 = "IPv4"
    PROTOCOL_IPV6 = "IPv6"
    PROTOCOL_CHOICES = (
        (PROTOCOL_BOTH, "Both"),
        (PROTOCOL_IPV4, PROTOCOL_IPV4),
        (PROTOCOL_IPV6, PROTOCOL_IPV6),
        )
    protocol = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        choices=PROTOCOL_CHOICES,
    )
    unpack_ipv4 = models.BooleanField(default=False)

    form_field_class = forms.GenericIPAddressField
    extra_form_field_names = [
        "protocol",
        "unpack_ipv4",
    ]


class MultipleChoiceField(ChoiceField):
    form_field_class = forms.MultipleChoiceField
    extra_form_field_names = []


class NullBooleanField(Field):
    form_field_class = forms.NullBooleanField
    extra_form_field_names = []


class RegexField(Field):
    regex = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD, blank=True)
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)
    strip = models.BooleanField(default=False)

    form_field_class = forms.RegexField
    extra_form_field_names = [
        "regex",
        "max_length",
        "min_length",
        "strip",
    ]


class SlugField(Field):
    allow_unicode = models.BooleanField(default=False)

    form_field_class = forms.SlugField
    extra_form_field_names = [
        "allow_unicode",
    ]


class TimeField(Field):
    form_field_class = forms.TimeField
    extra_form_field_names = []


class UrlField(Field):
    max_length = models.IntegerField(null=True, default=None, blank=True)
    min_length = models.IntegerField(null=True, default=None, blank=True)

    form_field_class = forms.URLField
    extra_form_field_names = [
        "max_length",
        "min_length",
    ]


class UuidField(Field):
    form_field_class = forms.UUIDField
    extra_form_field_names = []


class FilledForm(models.Model):
    slug = models.UUIDField(default=uuid.uuid4)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    time_completed = models.DateTimeField(null=True, blank=True)

    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.form, self.time_created)

    def save(self, *args, **kwargs):
        self.is_complete = self.check_complete()

        if self.is_complete:
            self.time_completed = self.time_completed or utils.timezone.now()

        result = super().save(*args, **kwargs)
        
        if not self.get_field_values().exists():
            self.create_field_values()

        return result

    def check_complete(self):
        field_values = self.get_field_values()

        if not field_values.exists():
            return False

        required_field_values = field_values.filter(field__required=True)
        return not required_field_values.filter(value="").exists()

    def create_field_values(self):
        fields = self.form.get_fields()
        field_value_class = self.get_field_value_class()

        for field in fields:
            field_value = field_value_class(
                **self.get_field_value_kwargs(
                    filled_form=self,
                    field=field,
                )
            )
            field_value.save()


    def get_data(self):
        return {
            field_value.field.get_attr_name(): field_value.value
            for field_value in self.get_field_values()
        }

    def get_field_values(self):
        return (
            self.get_field_value_class().objects
            .filter(filled_form=self)
            .order_by("pk")
        )

    def get_field_value_kwargs(self, **kwargs):
        return kwargs

    def get_field_value_class(self):
        return FieldValue


class FieldValue(models.Model):
    filled_form = models.ForeignKey(FilledForm, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.TextField(blank=True)
