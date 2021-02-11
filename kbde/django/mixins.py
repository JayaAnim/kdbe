from django import http, urls
from django.core import exceptions
from django.contrib.auth import mixins as auth_mixins
from django.contrib.staticfiles import finders
from django.templatetags import static
from django.contrib.postgres import search as pg_search
from django.conf import settings

from kbde.import_tools import utils as import_utils
from kbde.django import permissions

import inspect


class PostToGet:
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class Permissions:
    permission_classes = None

    def dispatch(self, *args, **kwargs):
        return self.check_permissions() or super().dispatch(*args, **kwargs)

    def check_permissions(self):
        """
        Check all permissions in self.permission_classes
        Calls permission.check() on each permission.
        Returns the first result of those calls which is not True
        If they are all true, returns None
        """
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

            if result is not None:
                return result

        return None

    def get_permission_classes(self):
        if self.permission_classes is not None:
            return self.permission_classes

        return settings.DEFAULT_PERMISSION_CLASSES


class UserAllowedInstances:
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
        


class Base(Permissions):
    page_template_name = getattr(settings, "PAGE_TEMPLATE_NAME", None) or "kbde/page.html"

    @classmethod
    def get_urls_path(cls, url_path, **view_kwargs):
        if hasattr(cls, "template_name"):
            view_kwargs.setdefault("template_name", cls.page_template_name)

        return urls.path(
            url_path,
            cls.as_view(**view_kwargs),
            name=cls.__name__,
        )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["content_template_name"] = self.get_kbde_template_name()
        return context_data

    def get_template_names(self):
        return [
            getattr(self, "template_name", None) or
            self.get_kbde_template_name()
        ]

    def get_kbde_template_name(self):
        path_name = self.__class__.__name__

        # Template name is {module_name}/{path_name}.html
        module_name_list = self.__class__.__module__.split(".")[:-1]
        module_name = "/".join(module_name_list)
        template_name = f"{module_name}/{path_name}.html"

        return template_name


class OpenGraph:
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


class Delete:
    previous_url = None
    prompt_text = "Are you sure that you want to delete {}?"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data.update({
            "prompt_text": self.get_prompt_text(),
            "previous_url": self.get_previous_url(),
        })

        return data

    def get_prompt_text(self):
        return self.prompt_text.format(self.object)

    def get_previous_url(self):
        return self.previous_url


class EmailForm:
    
    def form_valid(self, form):
        # Send the email via the form
        form.send_email()
        return super().form_valid(form)


class RelatedObject:
    related_model = None
    related_orm_path = None

    def get_queryset(self):
        queryset = super().get_queryset()

        related_orm_path = self.get_related_orm_path()
        related_object = self.get_related_object()
        
        return queryset.filter(**{related_orm_path: related_object})

    def get_related_orm_path(self):
        assert self.related_orm_path, (
            f"{self.__class__} must define "
             "`.related_orm_path` or override "
             "`.get_related_orm_path()`"
        )

        return self.related_orm_path

    def get_related_object(self):
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


class RelatedObjectEdit(RelatedObject):
    
    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        if hasattr(form, "instance"):

            related_orm_path = self.get_related_orm_path()

            if "__" not in related_orm_path:
                setattr(form.instance, related_orm_path, self.get_related_object())

        return form

    def perform_create(self, serializer):
        kwargs = {}

        related_orm_path = self.get_related_orm_path()

        if "__" not in related_orm_path:
            kwargs[related_orm_path] = self.get_related_object()

        serializer.save(**kwargs)


class SoftDelete:
    
    def get_queryset(self):
        q = super().get_queryset()
        return q.filter(deleted=False)


class SearchQueryset:
    search_url_kwarg = "search"
    search_vector_args = None

    def get_queryset(self):
        assert self.search_vector_args, (
            f"{self.__class__} must define `.search_vector_args`"
        )

        q = super().get_queryset()

        search = self.request.GET.get(self.search_url_kwarg)

        if search:
            q = q.annotate(
                search=pg_search.SearchVector(*self.search_vector_args)
            ).filter(search=search)

        return q


class SuccessUrlNext:
    
    def get_success_url(self):
        return self.request.GET.get("next") or super().get_success_url()
