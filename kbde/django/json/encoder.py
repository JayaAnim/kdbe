from django import forms
from django.db.models import query
from django.db.models.fields import files
from django.core.files import uploadedfile
from django.utils import functional

from kbde.json import encoder


class QuerySetSerializer(encoder.SerializerBase):

    def serialize(self):
        return list(self.val)


class PromiseSerializer(encoder.SerializerBase):
    
    def serialize(self):
        return self.val.__str__()


class FieldFileSerializer(encoder.SerializerBase):
    
    def serialize(self):
        if self.val:
            return self.val.url


class UploadedFileSerializer(encoder.SerializerBase):

    def serialize(self):
        return ""


class FormSerializer(encoder.SerializerBase):
    
    def serialize(self):
        form = self.val

        data = {}

        if form.errors:
            data["errors"] = form.errors

        if not hasattr(form, "cleaned_data") or form.errors:
            data["data"] = self.get_form_data(form)
            data["fields"] = self.get_form_fields(form)

        return data

    def get_form_data(self, form):
        return {
            field_name: form[field_name].value()
            for field_name in form.fields
        }

    def get_form_fields(self, form):
        form_fields = []

        for field_name in form.fields:
            bound_field = form[field_name]
            bound_field.field.name = field_name

            form_fields.append(bound_field)

        return form_fields


class FormFieldSerializer(encoder.SerializerBase):
    all_field_attrs = [
        "name",
        "required",
        "label",
        "label_suffix",
        "initial",
        "help_text",
        "disabled",
    ]

    field_attr_map = {
        forms.CharField: [
            "min_length",
            "max_length",
            "empty_value",
        ],
        forms.ChoiceField: [
            "choices",
        ],
        forms.TypedChoiceField: [
            "choices",
            "empty_value",
        ],
        forms.DateField: [
            "input_formats",
        ],
        forms.DateTimeField: [
            "input_formats",
        ],
        forms.DecimalField: [
            "min_value",
            "max_value",
            "max_digits",
            "decimal_places",
        ],
        forms.IntegerField: [
            "min_value",
            "max_value",
        ],
        forms.MultipleChoiceField: [
            "choices",
        ],
        forms.RegexField: [
            "regex",
            "strip",
        ],
        forms.SlugField: [
            "allow_unicode",
            "empty_value",
        ],
        forms.TimeField: [
            "input_formats",
        ],
        forms.URLField: [
            "min_length",
            "max_length",
            "empty_value",
        ],
    }
    
    def serialize(self):
        bound_field = self.val

        field_description_data = self.get_field_description_data(
            bound_field.field,
        )

        field_description_data["input_type"] = getattr(
            bound_field.field.widget,
            "input_type",
            None,
        )

        return field_description_data

    def get_field_description_data(self, field):
        # Get the fields that are present on all fields
        all_field_attrs = self.get_all_field_attrs()
        description_data = {
            field_attr: getattr(field, field_attr)
            for field_attr in all_field_attrs
        }

        # Get the fields which are specific to this type of field
        field_attr_map = self.get_field_attr_map()
        field_attrs = field_attr_map.get(field.__class__, [])

        description_data.update({
            field_attr: getattr(field, field_attr)
            for field_attr in field_attrs
            if hasattr(field, field_attr)
        })

        for field_attr, value in description_data.items():
            if callable(value):
                value = value()

            description_data[field_attr] = value

        if isinstance(field.widget, forms.ClearableFileInput):
            description_data["clear_field_name"] = f"{field.name}-clear"

        return description_data

    def get_all_field_attrs(self):
        return self.all_field_attrs

    def get_field_attr_map(self):
        return self.field_attr_map


class Encoder(encoder.Encoder):
    type_serializer_map = {
        query.QuerySet: QuerySetSerializer,
        functional.Promise: PromiseSerializer,
        files.FieldFile: FieldFileSerializer,
        uploadedfile.TemporaryUploadedFile: UploadedFileSerializer,
        uploadedfile.InMemoryUploadedFile: UploadedFileSerializer,
        uploadedfile.SimpleUploadedFile: UploadedFileSerializer,
        forms.BaseForm: FormSerializer,
        forms.BoundField: FormFieldSerializer,
        **encoder.Encoder.type_serializer_map,
    }
