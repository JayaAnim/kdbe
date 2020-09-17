from django import views, urls, apps, http, forms
from django.conf import settings
from kbde.django import mixins as kbde_mixins

from . import models


class ImportFileCreate(views.generic.CreateView):
    template_name = "kbde_django_db_import/import_file/create.html"
    model = models.ImportFile
    fields = [
        "name",
        "source",
    ]
    success_url = urls.reverse_lazy("kbde_django_db_import:file_list")


class ImportFileList(views.generic.ListView):
    template_name = "kbde_django_db_import/import_file/list.html"
    model = models.ImportFile
    paginate_by = 10
    ordering = ["-pk"]


class ImportRowList(kbde_mixins.RelatedObject, views.generic.ListView):
    template_name = "kbde_django_db_import/import_row/list.html"
    model = models.ImportRow
    related_orm_path = "import_file"
    related_model = models.ImportFile
    paginate_by = 10
    ordering = ["-pk"]


class ImportMappingTypeSelect(views.generic.TemplateView):
    template_name = "kbde_django_db_import/import_mapping/type_select.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data["mapping_types"] = self.get_mapping_types()

        return context_data

    def get_mapping_types(self):
        allowed_models = settings.IMPORT_MAPPING_MODELS

        models = []

        for model_name in allowed_models:
            
            app_name, model_name = model_name.split(".")

            model = apps.apps.get_model(app_name, model_name)

            models.append(model)

        return models

class ImportMappingCreate(views.generic.CreateView):
    template_name = "kbde_django_db_import/import_mapping/create.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)

        form.fields["import_file"].queryset = form.fields["import_file"].queryset.order_by("-pk")

        self.model().modify_form(form)

        return form

    def get_form_class(self):
        self.model = self.get_model()
        self.fields = self.model.form_field_names

        return super().get_form_class()
        
    def get_model(self):
        model_name = self.get_model_name()

        return apps.apps.get_model(model_name)

    def get_model_name(self):
        allowed_models = settings.IMPORT_MAPPING_MODELS

        model_name = self.kwargs.get("model_name")

        assert model_name is not None, f"{self.__class__.__name__} must define a URL param `model_name`"
        
        for app_model_name in allowed_models:

            app_name, model_n = app_model_name.split(".")
            
            if model_name == model_n:
                return app_model_name

        raise http.Http404(f"Import type `{model_name}` not found")

    def get_success_url(self):
        return urls.reverse(
            "kbde_django_db_import:mapping_column_list",
            args=[self.object.pk]
        )


class ImportMappingList(views.generic.ListView):
    template_name = "kbde_django_db_import/import_mapping/list.html"
    model = models.ImportMapping
    paginate_by = 10
    ordering = ["-pk"]


class ImportMappingColumnList(kbde_mixins.RelatedObject, views.generic.ListView):
    template_name = "kbde_django_db_import/import_mapping_column/list.html"
    model = models.ImportMappingColumn
    related_orm_path = "mapping"
    related_model = models.ImportMapping
    paginate_by = 10
    ordering = ["-pk"]


class ImportMappingColumnCreate(kbde_mixins.RelatedObjectEdit, views.generic.CreateView):
    template_name = "kbde_django_db_import/import_mapping_column/create.html"
    model = models.ImportMappingColumn
    related_orm_path = "mapping"
    related_model = models.ImportMapping
    fields = [
        "column",
        "import_field",
        "is_identifier",
    ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        
        form.fields["import_field"] = self.get_import_fields_field()
        form.fields["column"].queryset = form.fields["column"].queryset.filter(
            import_file=self.get_related_object().import_file
        )

        return form

    def get_import_fields_field(self):
        return forms.ChoiceField(
            choices=self.get_import_field_choices(),
        )

    def get_import_field_choices(self):
        import_mapping = self.get_related_object()
        return ((field, field) for field in import_mapping.import_fields)

    def get_success_url(self):
        return urls.reverse(
            "kbde_django_db_import:mapping_column_list",
            args=[self.object.mapping.pk]
        )


class ImportMappingRowList(kbde_mixins.RelatedObject, views.generic.ListView):
    template_name = "kbde_django_db_import/import_mapping_row/list.html"
    model = models.ImportMappingRow
    related_orm_path = "mapping"
    related_model = models.ImportMapping
    paginate_by = 10
    ordering = ["-pk"]


class ImportMappingComplete(views.generic.UpdateView):
    template_name = "kbde_django_db_import/import_mapping/complete.html"
    model = models.ImportMapping
    fields = []
    success_url = urls.reverse_lazy("kbde_django_db_import:mapping_list")


class ImportCreate(views.generic.CreateView):
    template_name = "kbde_django_db_import/import/create.html"
    model = models.Import
    fields = [
        "import_mapping",
    ]
    success_url = urls.reverse_lazy("kbde_django_db_import:list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)

        form.fields["import_mapping"].queryset = form.fields["import_mapping"].queryset.filter(
            bg_process_status=models.ImportMapping.BG_PROCESS_STATUS_COMPLETED
        ).order_by("-pk")

        return form


class ImportList(views.generic.ListView):
    template_name = "kbde_django_db_import/import/list.html"
    model = models.Import
    paginate_by = 10
    ordering = ["-pk"]
