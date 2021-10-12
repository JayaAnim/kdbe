from django import views, template, utils
from django.contrib.auth import views as auth_views

from . import mixins
from .. import forms

import math


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
    pages_to_show = 5

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update(self.get_pagination_context_data(context_data))

        return context_data

    def get_pagination_context_data(self, context_data):
        return {
            "page_numbers": self.get_page_numbers(context_data),
            "extra_params": self.get_extra_params_str(),
        }

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

    def get_page_numbers(self, context_data):
        page_obj = context_data.get("page_obj")

        if page_obj is None:
            return None

        pages_to_show = self.get_pages_to_show()

        first_page = int(page_obj.paginator.num_pages - (pages_to_show / 2))
        last_page = math.ceil(page_obj.paginator.num_pages + (pages_to_show / 2))

        page_offset = 1 - first_page

        adjusted_first_page = first_page + page_offset
        adjusted_last_page = last_page + page_offset

        if page_obj.paginator.num_pages < adjusted_last_page:
            adjusted_last_page = page_obj.paginator.num_pages

        return range(adjusted_first_page, adjusted_last_page+1)

    def get_pages_to_show(self):
        return self.pages_to_show

    def get_extra_params_str(self):
        extra_params = self.get_extra_params()
        extra_params = [f"{key}={value}" for key, value in extra_params.items()]

        extra_params_str = "&".join(extra_params)

        if extra_params_str:
            extra_params_str = f"&{extra_params_str}"

        return extra_params_str

    def get_extra_params(self):
        extra_params = {key: self.request.GET[key] for key in self.request.GET}
        extra_params.pop("page", None)
        return extra_params


class FormView(mixins.Form, mixins.Base, views.generic.FormView):
    pass


class CreateView(mixins.Form, mixins.Base, views.generic.CreateView):
    pass


class UpdateView(mixins.Form,
                 mixins.UserAllowedQueryset,
                 mixins.Base,
                 views.generic.UpdateView):

    def get_object(self, *args, **kwargs):
        obj = self.kwargs.get("object")

        if obj is not None:
            return obj

        return super().get_object(*args, **kwargs)

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
    template_name = "kbde/views/MarkdownView.html"
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
    template_name = "kbde/views/Table.html"
    table_empty_message = None
    fields = None
    labels = None
    include_row_data = True

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
            "empty_message": self.get_table_empty_message(),
        }

    def get_label_list(self):
        labels = self.get_labels()
        return [labels[field] for field in self.get_fields()]

    def get_row_data_from_object(self, obj):
        return [
            self.get_value_from_object(obj, field) for field in self.get_fields()
        ]

    def get_value_from_object(self, obj, field):
        # Try to get with a getter method
        get_method_name = f"get_{field}"
        get_method = getattr(obj, get_method_name, not_found)
        if get_method != not_found:
            return get_method()

        # Get explicit value from the object
        explicit_value = getattr(obj, field, not_found)
        if explicit_value != not_found:
            return explicit_value

        assert False, (
            f"Could not get value for field `{field}` on object `{obj}`"
        )

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


class SearchFormView(FormView):
    form_class = forms.SearchForm
    method = "GET"
    permission_classes = []
    prompt_text = ""

    def get_initial(self):
        return self.request.GET
