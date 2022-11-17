from django import views, template, utils, http, urls
from django.apps import apps
from django.core import exceptions
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles import finders
from django.templatetags import static
from django.conf import settings

from kbde.django import permissions
from kbde.django import forms
from kbde.django import response as kbde_response

from kbde.import_tools import utils as import_utils

from urllib import parse

import math, uuid, inspect, importlib


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

        return getattr(settings, "DEFAULT_PERMISSION_CLASSES", None)


class UrlPathMixin:
        
    @classmethod
    def get_urls_path(cls, url_path, **view_kwargs):
        return urls.path(
            url_path,
            cls.as_view(**view_kwargs),
            name=cls.__name__,
        )


class MetaMixin:
    meta_tags = [
        {
            "charset": "utf-8",
        },
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, shrink-to-fit=no"
        },
    ]

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.is_page_view:
            context_data["meta_tags"] = self.get_meta_tags()

        return context_data

    def get_meta_tags(self):
        return self.meta_tags.copy()


class NoindexMixin(MetaMixin):
    noindex = True
    noindex_names = [
        "robots",
    ]

    def get_meta_tags(self):
        meta_tags = super().get_meta_tags()

        if self.get_noindex():
            
            noindex_names = self.get_noindex_names()

            assert noindex_names, (
                f"{self.__class__} must has the .noindex attribute set to "
                f"True, but it did not define any .noindex_names"
            )

            for noindex_name in noindex_names:
                meta_tags.append({
                    "name": noindex_name,
                    "content": "noindex",
                })

        return meta_tags

    def get_noindex(self):
        return self.noindex

    def get_noindex_names(self):
        return self.noindex_names.copy()


class PageTemplateMixin(UrlPathMixin, NoindexMixin):
    page_template_name = (
        getattr(settings, "PAGE_TEMPLATE_NAME", None)
        or "kbde/django/page.html"
    )
    template_name = None
    is_page_view = False

    @classmethod
    def get_urls_path(cls, url_path, **view_kwargs):
        view_kwargs["is_page_view"] = True

        return super().get_urls_path(url_path, **view_kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.is_page_view and self.get_page_template_name() is not None:
            context_data["content_template_name"] = self.get_content_template_name()

        return context_data

    def get_template_names(self):
        if self.is_page_view:
            template_name = self.get_page_template_name()

            if template_name is None:
                template_name = self.get_content_template_name()

        else:
            template_name = self.get_content_template_name()

        return [template_name]

    def get_page_template_name(self):
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


class PartialMixin:
    
    def setup(self, request, *args, **kwargs):

        if kwargs.get("render_partial_catalog"):
            kwargs = self.get_catalog_kwargs()

        return super().setup(request, *args, **kwargs)


class BackUrlMixin:
    
    def get_back_url_safe(self):
        return parse.quote_plus(self.get_back_url())

    def get_back_url(self):
        return self.request.get_full_path()


class RequestUrlHeaderMixin:
    
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)

        response["x-request-path"] = self.request.path

        return response


class BaseMixin(PartialMixin,
                RequestUrlHeaderMixin,
                PermissionsMixin,
                ViewIdMixin,
                BackUrlMixin,
                PageTemplateMixin):
    pass


class PostToGetMixin:
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class TemplateResponseMixin:
    response_class = kbde_response.TemplateResponse


class FormMixin(TemplateResponseMixin):
    template_name = "kbde/django/views/Form.html"
    prompt_text = None
    field_error_message = "Please resolve the issues below"
    submit_button_text = "GO"
    method = "POST"
    action = ""

    def post(self, *args, **kwargs):
        if self.request.POST.get("form_id") == self.get_form_id():
            response = super().post(*args, **kwargs)

            if (
                isinstance(response, http.HttpResponseRedirect)
                and not self.is_page_view
            ):
                # This form is trying to redirect, but is being rendered as a
                # partial. Raise an exception to propagate this redirect to
                # the browser
                raise self.Redirect(response.url)

            return response

        else:
            return self.get(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.POST.get("form_id") != self.get_form_id():
            # Pop args to prevent the form from being bound
            kwargs.pop("data", None)
            kwargs.pop("files", None)

        return kwargs
    
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        
        context_data.update({
            "prompt_text": self.get_prompt_text(),
            "field_error_message": self.get_field_error_message(),
            "submit_button_text": self.get_submit_button_text(),
            "method": self.get_method(),
            "action": self.get_action(),
            "form_id": self.get_form_id(),
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

    def get_form_id(self):
        return self.__class__.__name__

    def get_success_url(self):
        success_url = self.kwargs.get("success_url")

        if success_url is not None:
            return success_url

        return super().get_success_url()

    class Redirect(Exception):
        pass


class DeleteMixin(FormMixin):
    prompt_text = "Delete {obj}?"
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


class OpenGraphMixin(MetaMixin):
    """
    A view mixin which enables OG
    """
    open_graph = {}

    def get_meta_tags(self):
        meta_tags = super().get_meta_tags()

        open_graph = self.get_open_graph()

        # Allow images to be staticfile references
        image = open_graph.get("og:image")

        if image and finders.find(image):
            open_graph["og:image"] = static.static(image)

        for prop, content in open_graph.items():
            meta_tags.append({
                "property": prop,
                "content": content,
            })

        return meta_tags

    def get_open_graph(self):
        assert self.open_graph, (
            f"{self.__class__} must define .open_graph"
        )

        return self.open_graph.copy()


class RelatedObjectMixin:
    related_model = None
    related_orm_path = None
    related_slug_field = "slug"

    def get(self, *args, **kwargs):
        self.related_object = self.get_related_object()
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        super_post = getattr(super(), "post", None)

        if super_post is None:
            return self.http_method_not_allowed(*args, **kwargs)

        self.related_object = self.get_related_object()

        return super_post(*args, **kwargs)

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
            related_queryset = related_queryset.filter(
                **{self.related_slug_field: related_slug},
            )

        try:
            obj = related_queryset.get()
        except related_queryset.model.DoesNotExist:
            raise http.Http404(
                f"No related {related_queryset.model._meta.verbose_name}s "
                f"found matching the query"
            )
        
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

    def get_form_id(self):
        form_id = super().get_form_id()
        return f"{form_id}-{self.related_object.pk}"


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


class TemplateView(TemplateResponseMixin,
                   PostToGetMixin,
                   BaseMixin,
                   views.generic.TemplateView):
    pass


class RedirectView(BaseMixin, views.generic.RedirectView):
    pass


class DetailView(TemplateResponseMixin,
                 PostToGetMixin,
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


class ListView(TemplateResponseMixin,
               PostToGetMixin,
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

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super().post(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = self.kwargs.get("object")

        if obj is not None:
            return obj

        return super().get_object(*args, **kwargs)

    def get_queryset(self):
        return self.get_user_update_queryset()

    def get_form_id(self):
        form_id = super().get_form_id()
        return f"{form_id}-{self.object.pk}"


class DeleteView(DeleteMixin,
                 UserAllowedQuerysetMixin,
                 BaseMixin,
                 views.generic.DeleteView):

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super().post(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = self.kwargs.get("object")

        if obj is not None:
            return obj

        return super().get_object(*args, **kwargs)

    def get_queryset(self):
        return self.get_user_delete_queryset()

    def get_form_id(self):
        form_id = super().get_form_id()
        return f"{form_id}-{self.object.pk}"


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
    markdown_extensions = []

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["markdown"] = self.get_markdown(context_data)
        return context_data

    def get_markdown(self, context_data):
        markdown_template_name = self.get_markdown_template_name()
        markdown_content = template.loader.render_to_string(
            markdown_template_name,
            context_data,
        )

        html = self.convert_markdown(markdown_content)

        return utils.safestring.mark_safe(html)

    def get_markdown_template_name(self):
        return (
            self.markdown_template_name or 
            self.get_class_template_name(file_extension="md")
        )

    def convert_markdown(self, markdown_content):
        import markdown

        return markdown.markdown(
            markdown_content,
            extensions=self.get_markdown_extensions(),
        )

    def get_markdown_extensions(self):
        return self.markdown_extensions.copy()


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

                assert len(row_data) == len(label_list), (
                    f"{self.__class__}: get_row_data_from_object() must "
                    f"return a list of values that has the same number of "
                    f"entries as the label list ({len(label_list)})"
                )

                row["data"] = row_data

            row["tag_attrs"] = self.get_row_tag_attrs(obj)

            row_list.append(row)

        return {
            "labels": label_list,
            "rows": row_list,
            "empty_message": self.get_table_empty_message(),
        }

    def get_label_list(self):
        fields = self.get_fields()
        labels = self.get_labels()
        return [labels[field] for field in fields]

    def get_row_data_from_object(self, obj):
        return [
            self.get_value_from_object(obj, field)
            for field in self.get_fields()
        ]

    def get_value_from_object(self, obj, field):
        # Try to get with a getter method
        get_method_name = f"get_{field}"

        # Try to use the getter method on this class
        get_method = getattr(self, get_method_name, not_found)

        if get_method != not_found:
            return get_method(obj)

        # Try to use the getter method on the object
        obj_get_method = getattr(obj, get_method_name, not_found)

        if obj_get_method != not_found:
            return obj_get_method()

        # Get explicit value from the object
        explicit_value = getattr(obj, field, not_found)

        if explicit_value != not_found:
            return explicit_value

        assert False, (
            f"Could not get value for field `{field}` on object `{obj}`"
        )

    def get_row_tag_attrs(self, obj):
        return {}

    def get_table_empty_message(self):
        assert self.table_empty_message, (
            f"{self.__class__} must define .table_empty_message"
        )
        return self.table_empty_message

    def get_fields(self):
        assert self.fields is not None, (
            f"{self.__class__} must define .fields"
        )
        return self.fields.copy()

    def get_labels(self):
        assert self.labels is not None, (
            f"{self.__class__} must define .labels"
        )
        return self.labels.copy()


class Messages(TemplateView):
    template_name = "kbde/django/views/Messages.html"
    permission_classes = []


class PartialCatalog(ListView):
    template_name = "kbde/django/views/PartialCatalog.html"
    permission_classes = [
        permissions.DebugModeRequired,
    ]

    def get_queryset(self):
        return self.get_app_list()

    def get_app_list(self):
        single_class_path = self.request.GET.get("class_path")
        single_app_name = self.request.GET.get("app_name")

        app_list = []

        for app_config in apps.get_app_configs():
            
            if single_app_name and app_config.name != single_app_name:
                continue

            try:
                partials = importlib.import_module(f"{app_config.name}.partials")
            except ModuleNotFoundError:
                continue

            partial_class_paths = []

            for cls_name, cls in inspect.getmembers(partials, inspect.isclass):
                partial_class_path = f"{cls.__module__}.{cls.__name__}"

                if single_class_path and partial_class_path != single_class_path:
                    continue

                if cls.__module__ != partials.__name__:
                    continue

                get_catalog_kwargs = getattr(cls, "get_catalog_kwargs", None)

                if get_catalog_kwargs is None:
                    continue

                partial_class_paths.append(partial_class_path)

            if not partial_class_paths:
                continue

            partial_class_paths.sort()

            app_list.append({
                "name": app_config.name,
                "partial_class_paths": partial_class_paths,
            })

        return sorted(app_list, key=lambda app: app["name"])


class RequiredKwargsMixin:
    """
    Defines a set of required kwarg keys that must be passed to the view,
    either from a url or from render_partial.

    Raises an error if a kwarg is missing.

    Merges all required kwargs into context_data.
    """
    required_kwarg_keys = None

    def get(self, *args, **kwargs):
        self.required_kwargs = self.get_required_kwargs()

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.required_kwargs = self.get_required_kwargs()

        return super().post(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        # We update context_data over required_kwargs so that any conflicts
        # between the two will take the existing context_data
        new_context_data = {}
        new_context_data.update(self.required_kwargs)
        new_context_data.update(context_data)

        return new_context_data

    def get_required_kwargs(self):
        required_kwarg_keys = self.get_required_kwarg_keys()

        required_kwargs = {}

        for key in required_kwarg_keys:
            value = self.get_required_kwarg_value(key)

            assert value != not_found, (
                f"{self.__class__} missing required kwarg `{key}`"
            )

            required_kwargs[key] = value

        return required_kwargs

    def get_required_kwarg_value(self, key):
        return self.kwargs.get(key, not_found)

    def get_required_kwarg_keys(self):
        assert self.required_kwarg_keys is not None, (
            f"{self.__class__} must define .required_kwarg_keys or override "
            f".get_required_kwarg_keys()"
        )
        return self.required_kwarg_keys.copy()


class RequiredGetKwargsMixin(RequiredKwargsMixin):

    def get_required_kwarg_value(self, key):
        value = super().get_required_kwarg_value(key)

        if value != not_found:
            return value

        value = self.request.GET.get(key, not_found)

        if value == not_found:
            raise exceptions.SuspiciousOperation(
                f"Missing argument `{key}`"
            )

        return value


class AjaxMixin:
    page_template_name = "kbde/django/views/ajax_page.html"
    ajax_template_name = "kbde/django/views/ajax.html"
    action_url = None
    handle_post = True

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            "ajax_content_template_name": self.get_ajax_content_template_name(),
            "action_url": self.get_action_url(),
            "handle_post": self.get_handle_post(),
        })

        return context_data

    def get_ajax_content_template_name(self):
        return self.get_content_template_name()

    def get_template_names(self):
        if self.is_page_view:
            template_name = self.get_page_template_name()
        else:
            template_name = self.get_ajax_template_name()

        return [template_name]

    def get_ajax_template_name(self):
        return self.ajax_template_name
    
    def get_action_url(self):
        assert self.action_url is not None, (
            f"{self.__class__} must define .action_url or override "
            f".get_action_url()"
        )
        return self.action_url

    def get_handle_post(self):
        return self.handle_post


class RobotsTxt(TemplateView):
    page_template_name = None
    content_type = "text/plain"
    permission_classes = []

    def get_content_template_name(self, file_extension="txt", *args, **kwargs):
        return super().get_content_template_name(
            file_extension=file_extension,
            *args,
            **kwargs,
        )
