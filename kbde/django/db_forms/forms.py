from django import forms

from . import models


class FilledFormUpdate(forms.Form):
    
    def __init__(self, instance, initial=None, *args, **kwargs):
        self.instance = instance

        initial = initial or self.instance.get_data()

        super().__init__(initial=initial, *args, **kwargs)

        self.add_fields()

    def add_fields(self):
        field_values = self.instance.get_field_values()

        for field_value in field_values:
            self.fields[field_value.field.get_attr_name()] = (
                field_value.field.get_form_field()
            )

    def save(self, *args, **kwargs):
        self.instance.save()

        no_obj = object()

        for field_value in self.instance.get_field_values():
            value = self.cleaned_data.get(
                field_value.field.get_attr_name(),
                no_obj,
            )

            if value == no_obj:
                continue

            field_value.value = value

            field_value.save()

        self.instance.save()

        return self.instance
