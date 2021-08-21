from django import views, template, utils
from django.contrib.auth import views as auth_views

from . import mixins
from .. import forms


not_found = object()


class View(mixins.Base, views.generic.View):
    pass


class TemplateView(mixins.PostToGet, mixins.Base, views.generic.TemplateView):
    pass


class RedirectView(mixins.Base, views.generic.RedirectView):
    pass


class DetailView(mixins.PostToGet,
                 mixins.UserAllowedQueryset,
                 mixins.Base,
                 views.generic.DetailView):

    def get_object(self, *args, **kwargs):
        obj = self.kwargs.get("object")

        if obj is not None:
            return obj

        return super().get_object(*args, **kwargs)

    def get_queryset(self):
        return self.get_user_read_queryset()


class ListView(mixins.PostToGet,
               mixins.UserAllowedQueryset,
               mixins.Base,
               views.generic.ListView):

    def get_queryset(self):
        object_list = self.kwargs.get("object_list")

        if object_list is not None:
            return object_list

        queryset = self.get_user_read_queryset()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


class FormView(mixins.Form, mixins.Base, views.generic.FormView):
    pass


class CreateView(mixins.Form, mixins.Base, views.generic.CreateView):
    pass


class UpdateView(mixins.Form,
                 mixins.UserAllowedQueryset,
                 mixins.Base,
                 views.generic.UpdateView):

    def get_queryset(self):
        return self.get_user_update_queryset()


class DeleteView(mixins.Delete,
                 mixins.UserAllowedQueryset,
                 mixins.Base,
                 views.generic.DeleteView):

    def get_queryset(self):
        return self.get_user_delete_queryset()


# Auth


class LoginView(mixins.Form, mixins.Base, auth_views.LoginView):
    permission_classes = []


# Custom Views


class MarkdownView(TemplateView):
    """
    A component view which renders a markdown_template into HTML
    """
    template_name = "kbde/MarkdownView.html"
    markdown_template_name = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["markdown"] = self.get_markdown(context_data)
        return context_data

    def get_markdown(self, context_data):
        import markdown

        markdown_template_name = self.get_markdown_template_name()
        markdown_content = template.loader.render_to_string(
            markdown_template_name,
            context_data,
        )

        html = markdown.markdown(markdown_content)

        return utils.safestring.mark_safe(html)

    def get_markdown_template_name(self):
        return (
            self.markdown_template_name or 
            self.get_class_template_name(file_extension="md")
        )


class TableView(ListView):
    template_name = "kbde/Table.html"
    table_head_template_name = "kbde/partials/table_head.html"
    table_row_template_name = "kbde/partials/table_row.html"
    table_empty_template_name = "kbde/partials/table_empty.html"
    table_class = "table"
    table_empty_message = None
    fields = None
    labels = None
    include_row_data = True
    paginate = True
    pages_to_show = 5
    search_url_kwarg = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update(self.get_table(context_data["object_list"]))

        return context_data

    def get_table(self, object_list):
        label_list = self.get_label_list()

        row_list = []
        for obj in object_list:
            row = {
                "object": obj,
            }

            if self.include_row_data:
                row_data = self.get_row_data_from_object(obj)
                assert len(row_data) == len(label_list)
                row["data"] = row_data

            row_list.append(row)

        return {
            "labels": label_list,
            "rows": row_list,
            "table_head_template_name": self.get_table_head_template_name(),
            "table_row_template_name": self.get_table_row_template_name(),
            "table_empty_template_name": self.get_table_empty_template_name(),
            "table_class": self.get_table_class(),
            "empty_message": self.get_table_empty_message(),
            "paginate": self.get_paginate(),
            "pages_to_show": self.get_pages_to_show(),
            "extra": self.get_extra(),
        }

    def get_label_list(self):
        labels = self.get_labels()
        return [labels[field] for field in self.get_fields()]

    def get_row_data_from_object(self, obj):
        return [
            self.get_value_from_object(obj, field) for field in self.get_fields()
        ]

    def get_value_from_object(self, obj, field):
        explicit_value = getattr(obj, field, not_found)
        if explicit_value != not_found:
            return explicit_value

        # Try to get with a getter method
        get_method_name = f"get_{field}"
        get_method = getattr(obj, get_method_name, not_found)
        if get_method != not_found:
            return get_method()

        assert False, (
            f"Could not get value for field `{field}` on object `{obj}`"
        )

    def get_table_head_template_name(self):
        return self.table_head_template_name

    def get_table_row_template_name(self):
        return self.table_row_template_name

    def get_table_empty_template_name(self):
        return self.table_empty_template_name

    def get_table_class(self):
        return self.table_class

    def get_table_empty_message(self):
        assert self.table_empty_message, (
            f"{self.__class__} must define .table_empty_message"
        )
        return self.table_empty_message

    def get_fields(self):
        assert self.fields, (
            f"{self.__class__} must define .fields"
        )
        return self.fields

    def get_labels(self):
        assert self.labels, (
            f"{self.__class__} must define .labels"
        )
        return self.labels

    def get_paginate(self):
        return self.paginate

    def get_pages_to_show(self):
        return self.pages_to_show

    def get_extra(self):
        extra_kwargs = self.get_extra_kwargs()
        extra_args = [f"{key}={value}" for key, value in extra_kwargs.items()]

        return "&".join(extra_args)

    def get_extra_kwargs(self):
        extra_kwargs = {key: self.request.GET[key] for key in self.request.GET}
        extra_kwargs.pop("page", None)
        return extra_kwargs


class SearchFormView(FormView):
    form_class = forms.SearchForm
    method = "GET"
    permission_classes = []
    prompt_text = ""

    def get_initial(self):
        return self.request.GET


class ModalView(TemplateView):
    template_name = "kbde/ModalView.html"
    modal_button_text = None
    default_modal_button_class = "btn btn-primary"
    modal_header_text = None
    modal_body_template_name = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            "modal_button_text": self.get_modal_button_text(),
            "modal_button_class": self.get_modal_button_class(),
            "modal_header_text": self.get_modal_header_text(),
            "modal_body_template_name": self.get_modal_body_template_name(),
        })

        return context_data

    def get_modal_button_text(self):
        assert self.modal_button_text is not None, (
            f"{self.__class__} must define .modal_button_text or override "
            f".get_modal_button_text()"
        )
        return self.modal_button_text

    def get_modal_button_class(self):
        return self.kwargs.get(
            "modal_button_class",
            self.default_modal_button_class,
        )

    def get_modal_header_text(self):
        assert self.modal_header_text is not None, (
            f"{self.__class__} must define .modal_header_text or "
            f"override .get_modal_header_text()"
        )
        return self.modal_header_text

    def get_modal_body_template_name(self):
        assert self.modal_body_template_name is not None, (
            f"{self.__class__} must define .modal_body_template_name or "
            f"override .get_modal_body_template_name()"
        )
        return self.modal_body_template_name
