from django import forms
import json


class Flatpickr(forms.widgets.DateTimeInput):
    template_name = "kbde/forms/widgets/flatpickr.html"

    class Media:
        css = {
            "all": ("kbde/css/flatpickr.min.css",),
            }
        js = (
            "kbde/js/flatpickr.min.js",
            )

    def __init__(self, attrs=None, format=None, options=None):
        super().__init__(attrs=attrs, format=format)

        self.options = options

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["options"] = json.dumps(self.options or {})
        return context
