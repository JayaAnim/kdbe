from django import views, shortcuts

from . import models, forms


class FormMixin:
    template_name = "database_forms/form.html"
    model = models.FilledForm
    form_class = forms.Form
    form_title = None
    form_button_title = "Submit"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["form_title"] = self.get_form_title()
        data["form_button_title"] = self.get_form_button_title()

        return data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["form_instance"] = self.get_form_instance()

        return kwargs
    
    def get_queryset(self):
        q = super().get_queryset()
        return q.filter(form=self.get_form_instance())
    
    def get_form_instance(self):
        form_slug = self.kwargs.get("form_slug")
        return shortcuts.get_object_or_404(models.Form, slug=form_slug)

    def get_form_title(self):
        return self.form_title

    def get_form_button_title(self):
        return self.form_button_title


class Create(FormMixin, views.generic.edit.CreateView):
    pass


class Update(FormMixin, views.generic.edit.UpdateView):
    pass
