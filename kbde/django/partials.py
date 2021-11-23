from . import views


class FormFieldPartial(views.TemplateView):
    template_name = 'kbde/django/partials/FormField.html'

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)

        data['field'] = self.kwargs['field']

        return data

