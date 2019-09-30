from django import forms

from . import models


class Form(forms.Form):
    
    def __init__(self, form_instance, instance, initial=None, *args, **kwargs):
        self.form_instance = form_instance
        self.instance = instance or models.FilledForm()

        object_data = self.instance.get_data()

        if initial is not None:
            object_data.update(initial)

        super().__init__(initial=object_data, *args, **kwargs)

        self.add_fields()

    def add_fields(self):
        field_instances = self.form_instance.get_fields()

        for field_instance in field_instances:
            self.fields[field_instance.get_attr_name()] = field_instance.get_form_field()

    def save(self, *args, **kwargs):
        self.instance.form = self.form_instance

        self.instance.save()

        no_obj = object()
        for field_instance in self.form_instance.get_fields():
            value = self.cleaned_data.get(field_instance.get_attr_name(), no_obj)

            if value == no_obj:
                continue

            try:
                field_value = models.FieldValue.objects.get(filled_form=self.instance,
                                                            field=field_instance)
            except models.FieldValue.DoesNotExist:
                field_value = models.FieldValue(filled_form=self.instance,
                                                field=field_instance)

            field_value.value = self.data[field_instance.get_attr_name()]

            field_value.save()

        return self.instance
