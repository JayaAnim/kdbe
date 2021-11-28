from django import views, template, utils, http, urls
from django.core import exceptions
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles import finders
from django.templatetags import static
from django.conf import settings

from kbde.django import permissions
from kbde.django import forms

from kbde.import_tools import utils as import_utils

import math, uuid


not_found = object()


class ViewIdMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid.uuid4()


class PermissionsMixin:
    permission_classes = None

    def dispatch(self, *args, **kwargs):
        return (
            self.check_permissions(is_dispatching=True) or
            super().dispatch(*args, **kwargs)
        )

    def check_permissions(self, is_dispatching=False):
        """
        Check all permissions in self.permission_classes
        Calls permission.check() on each permission.
        Returns the first result of those calls which is not True
        If they are all True, returns None
        """
        self.is_dispatching = is_dispatching
        permission_classes = self.get_permission_classes()

        assert permission_classes is not None, (
            f"{self.__class__} must define an iterable, .permission_classes "
            f"or you must define settings.DEFAULT_PERMISSION_CLASSES "
            f"as an iterable of strings"
        )

        for permission_class in permission_classes:
            if isinstance(permission_class, str):
                # Import the class based on the string
                permission_class = import_utils.import_class_from_string(
                    permission_class,
                )

            assert issubclass(permission_class, permissions.Permission), (
                f"Class {permission_class} must be a subclass of "
                f"{permissions.Permission}"
            )
                
            result = permission_class().check(self)

            assert result is None or isinstance(result, http.HttpResponse), (
                f"{permission_class} .check() must return either "
                f"None or a response object"
            )

            if result is not None:
                return result

        return None

    def get_permission_classes(self):
        if self.permission_classes is not None:
            return self.permission_classes

        return settings.DEFAULT_PERMISSION_CLASSES


class UrlPathMixin:
        
    @classmethod
    def get_urls_path(cls, url_path, **view_kwargs):
        return urls.path(
            url_path,
            cls.as_view(**view_kwargs),
            name=cls.__name__,
        )


class PageTemplateMixin(UrlPathMixin):
    page_template_name = getattr(settings, "PAGE_TEMPLATE_NAME", None) or "kbde/django/page.html"
    template_name = None
    is_page_view = False

    @classmethod
    def get_urls_path(cls, url_path, **view_kwargs):
        view_kwargs["is_page_view"] = True

        return super().get_urls_path(url_path, **view_kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.is_page_view:
            context_data["content_template_name"] = self.get_content_template_name()

        return context_data

    def get_template_names(self):
        if self.is_page_view:
            template_name = self.get_page_template_name()
        else:
            template_name = self.get_content_template_name()

        return [template_name]

    def get_page_template_name(self):
        assert self.page_template_name, (
            f"{self.__class__} must define .page_template_name"
        )
        return self.page_template_name

    def get_content_template_name(self, file_extension="html"):
        return (
            self.template_name or
            self.get_class_template_name(file_extension)
        )

    def get_class_template_name(self, file_extension):
        path_name = self.__class__.__name__

        # Template name is {module_name}/{path_name}.html
        module_name_list = self.__class__.__module__.split(".")

        module_name = "/".join(module_name_list)
        template_name = f"{module_name}/{path_name}.{file_extension}"

        return template_name


class BaseMixin(PermissionsMixin, ViewIdMixin, PageTemplateMixin):
    pass


class PostToGetMixin:
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class FormMixin:
    template_name = "kbde/django/views/Form.html"
    prompt_text = None
    field_error_message = "Please resolve the issues below"
    submit_button_text = "GO"
    method = "POST"
    action = ""
    
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        
        context_data.update({
            "prompt_text": self.get_prompt_text(),
            "field_error_message": self.get_field_error_message(),
            "submit_button_text": self.get_submit_button_text(),
            "method": self.get_method(),
            "action": self.get_action(),
        })

        return context_data

    def get_prompt_text(self):
        assert self.prompt_text is not None, (
            f"{self.__class__} must define .prompt_text or override .get_prompt_text()"
        )
        return self.prompt_text

    def get_field_error_message(self):
        return self.field_error_message

    def get_submit_button_text(self):
        return self.submit_button_text

    def get_method(self):
        return self.method

    def get_action(self):
        return self.action


class DeleteMixin(FormMixin):
    prompt_text = "Are you sure you want to delete {obj}?"
    submit_button_text = "Delete"

    def get_prompt_text(self):
        return self.prompt_text.format(obj=self.object)


class UserAllowedQuerysetMixin:
    """
    Provides methods to pull only model instances which the
        currently-logged-in user can interact with
    """

    def get_queryset(self):
        raise NotImplementedError(
            f"{self.__class__} must implement .get_queryset()"
        )

    def get_user_read_queryset(self):
        model = self.get_model()

        assert hasattr(model, "get_user_read_queryset"), (
            f"Model, {self.model}, must implement classmethod "
            f".get_user_read_queryset()"
        )
        return model.get_user_read_queryset(self.request.user)

    def get_user_update_queryset(self):
        model = self.get_model()

        assert hasattr(model, "get_user_update_queryset"), (
            f"Model, {self.model}, must implement classmethod "
            f".get_user_update_queryset()"
        )
        return model.get_user_update_queryset(self.request.user)

    def get_user_delete_queryset(self):
        model = self.get_model()

        assert hasattr(model, "get_user_delete_queryset"), (
            f"Model, {self.model}, must implement classmethod "
            f".get_user_delete_queryset()"
        )
        return model.get_user_delete_queryset(self.request.user)

    def get_model(self):
        assert getattr(self, "model", None), (
            f"{self.__class__} must define `.model`"
        )
        return self.model


class OpenGraphMixin:
    """
    A view mixin which enables OG
    """
    open_graph = {}

    def get_open_graph(self):
        open_graph = self.open_graph.copy()

        for prop, content in open_graph.items():
            open_graph[prop] = self.get_static_url(content)

        return open_graph

    def get_static_url(self, path):
        if finders.find(path):
            path = static.static(path)
        return path


class RelatedObjectMixin:
    related_model = None
    related_orm_path = None

    def dispatch(self, *args, **kwargs):
        self.related_object = self.get_related_object()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["related_object"] = self.related_object
        return context_data

    def get_queryset(self):
        return super().get_queryset().filter(
            **{self.get_related_orm_path(): self.related_object},
        )

    def get_related_orm_path(self):
        assert self.related_orm_path, (
            f"{self.__class__} must define "
             "`.related_orm_path` or override "
             "`.get_related_orm_path()`"
        )

        return self.related_orm_path

    def get_related_object(self):
        related_object = self.kwargs.get("related_object")

        if related_object is not None:
            return related_object

        related_queryset = self.get_related_queryset()

        related_pk = self.kwargs.get("related_pk")
        related_slug = self.kwargs.get("related_slug")

        assert related_pk is not None or related_slug is not None, (
            f"{self.__class__} must be called with either `related_pk` or "
            f"`related_slug` in the URLconf")

        if related_pk is not None:
            # Filter by pk
            related_queryset = related_queryset.filter(pk=related_pk)
        else:
            # Filter by slug
            related_slug_field = getattr(self, "related_slug_field", "slug")
            related_queryset = related_queryset.filter(**{related_slug_field: related_slug})

        try:
            obj = related_queryset.get()
        except related_queryset.model.DoesNotExist:
            raise http.Http404(f"No related {related_queryset.model._meta.verbose_name}s found matching the query")

        return obj

    def get_related_queryset(self):
        related_model = getattr(self, "related_model", None)
        related_queryset = getattr(self, "related_queryset", None)

        assert related_model is not None or related_queryset is not None, (""
            f"{self.__class__} must define `.related_model` or "
            f"`.related_queryset`")

        if related_queryset is not None:
            return related_queryset
        else:
            return related_model.objects.all()
    
    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        if hasattr(form, "instance"):
            related_orm_path = self.get_related_orm_path()

            if "__" not in related_orm_path:
                setattr(form.instance, related_orm_path, self.related_object)

        return form

    def perform_create(self, serializer):
        kwargs = {}

        related_orm_path = self.get_related_orm_path()

        if "__" not in related_orm_path:
            kwargs[related_orm_path] = self.related_object

        serializer.save(**kwargs)


class SuccessUrlNextMixin:

    def form_valid(self, form):
        response = super().form_valid(form)
        return self.get_next_response(response)

    def delete(self, *args, **kwargs):
        response = super().delete(*args, **kwargs)
        return self.get_next_response(response)

    def get_next_response(self, response):
        next_url = self.get_next_url()
        if next_url:
            response = http.HttpResponseRedirect(next_url)

        return response

    def get_next_url(self):
        return self.request.GET.get("next")


class SuccessUrlNextRequiredMixin(SuccessUrlNextMixin):
    success_url = "/"

    def get_next_url(self):
        next_url = super().get_next_url()
        
        if not next_url:
            raise exceptions.SuspiciousOperation(
                "Must be called with a `next` GET parameter"
            )

        return next_url


class View(BaseMixin, views.generic.View):
    pass


class TemplateView(PostToGetMixin, BaseMixin, views.generic.TemplateView):
    pass


class RedirectView(BaseMixin, views.generic.RedirectView):
    pass


class DetailView(PostToGetMixin,
                 UserAllowedQuerysetMixin,
                 BaseMixin,
                 views.generic.DetailView):

    def get_object(self, *args, **kwargs):
        obj = self.kwargs.get("object")

        if obj is not None:
            return obj

        return super().get_object(*args, **kwargs)

    def get_queryset(self):
        return self.get_user_read_queryset()


class ListView(PostToGetMixin,
               UserAllowedQuerysetMixin,
               BaseMixin,
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
        if pages_to_show > page_obj.paginator.num_pages:
            pages_to_show = page_obj.paginator.num_pages

        page_numbers = list(range(pages_to_show))

        first_page = page_obj.number - int((pages_to_show - 1) / 2)
        if first_page < 1:
            first_page = 1

        last_page = first_page + pages_to_show - 1
        if last_page > page_obj.paginator.num_pages:
            first_page = first_page - (last_page - page_obj.paginator.num_pages)

        return [p + first_page for p in page_numbers]

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


class FormView(FormMixin, BaseMixin, views.generic.FormView):
    pass


class CreateView(FormMixin, BaseMixin, views.generic.CreateView):
    pass


class UpdateView(FormMixin,
                 UserAllowedQuerysetMixin,
                 BaseMixin,
                 views.generic.UpdateView):

    def get_object(self, *args, **kwargs):
        obj = self.kwargs.get("object")

        if obj is not None:
            return obj

        return super().get_object(*args, **kwargs)

    def get_queryset(self):
        return self.get_user_update_queryset()


class DeleteView(DeleteMixin,
                 UserAllowedQuerysetMixin,
                 BaseMixin,
                 views.generic.DeleteView):

    def get_object(self, *args, **kwargs):
        obj = self.kwargs.get("object")

        if obj is not None:
            return obj

        return super().get_object(*args, **kwargs)

    def get_queryset(self):
        return self.get_user_delete_queryset()


# Auth


class LoginView(FormMixin, BaseMixin, auth_views.LoginView):
    permission_classes = []


# Custom Views


class MarkdownView(TemplateView):
    """
    A component view which renders a markdown_template into HTML
    """
    template_name = "kbde/django/views/MarkdownView.html"
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
    template_name = "kbde/django/views/Table.html"
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
            self.get_value_from_object(obj, field)
            for field in self.get_fields()
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
        return self.fields.copy()

    def get_labels(self):
        assert self.labels, (
            f"{self.__class__} must define .labels"
        )
        return self.labels.copy()


class SearchFormView(FormView):
    form_class = forms.SearchForm
    method = "GET"
    permission_classes = []
    prompt_text = ""

    def get_initial(self):
        return self.request.GET


class Messages(TemplateView):
    template_name = "kbde/django/views/Messages.html"
    permission_classes = []