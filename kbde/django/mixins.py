from django import http
from django.contrib.auth import mixins as auth_mixins
from django.contrib.staticfiles import finders
from django.templatetags import static

import inspect


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

    def get_queryset(self):
        queryset = super().get_queryset()

        for related_model_name, related_object in self.get_related_objects().items():
            related_orm_path = self.get_related_orm_path(related_model_name)
            queryset = queryset.filter(**{related_orm_path: related_object})

        return queryset

    def get_related_orm_path(self, related_model_name):
        related_orm_path = getattr(self, f"{related_model_name}_orm_path", None)

        assert related_orm_path, f"{self.__class__.__name__} must define `.{related_model_name}_orm_path`"

        return related_orm_path

    def get_related_objects(self):
        return {related_model_name: self.get_related_object(related_model_name) for
                related_model_name in self.get_related_model_names()}

    def get_related_object(self, related_model_name):
        related_queryset = self.get_related_querysets()[related_model_name]

        related_pk = self.kwargs.get(f"{related_model_name}_pk")
        related_slug = self.kwargs.get(f"{related_model_name}_slug")

        assert related_pk is not None or related_slug is not None, (
            f"{self.__class__.__name__} must be called with either `{related_model_name}_pk` or "
            f"`{related_model_name}_slug` in the URLconf")

        if related_pk is not None:
            # Filter by pk
            related_queryset = related_queryset.filter(pk=related_pk)
        else:
            # Filter by slug
            related_slug_field = getattr(self, f"{related_model_name}_slug_field", "slug")
            related_queryset = related_queryset.filter(**{related_slug_field: related_slug})

        try:
            obj = related_queryset.get()
        except related_queryset.model.DoesNotExist:
            raise http.Http404(f"No related {related_queryset.model._meta.verbose_name}s found matching the query")

        return obj

    def get_related_querysets(self):
        return {related_model_name: self.get_related_queryset(related_model_name) for 
                related_model_name in self.get_related_model_names()}

    def get_related_queryset(self, related_model_name):
        related_model = getattr(self, f"{related_model_name}_model", None)
        related_queryset = getattr(self, f"{related_model_name}_queryset", None)

        assert related_model is not None or related_queryset is not None, (""
            f"{self.__class__.__name__} must define `.{related_model_name}_model` or "
            f"`.{related_model_name}_queryset`")

        if related_queryset is not None:
            return related_queryset
        else:
            return related_model.objects.all()

    def get_related_model_names(self):
        """
        Get all attributes that end with `_orm_path`, and return the prefixes as model names
        """
        related_model_names = []

        members = inspect.getmembers(type(self), lambda member: not(inspect.isroutine(member)))

        for attr, value in members:

            if not attr.endswith("_orm_path"):
                continue

            related_model_name = attr.replace("_orm_path", "")

            if not related_model_name:
                continue

            related_model_names.append(related_model_name)

        return related_model_names


class RelatedObjectEdit(RelatedObject):
    
    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        if hasattr(form, "instance"):

            for related_model_name in self.get_related_model_names():

                related_orm_path = self.get_related_orm_path(related_model_name)

                if "__" in related_orm_path:
                    continue

                setattr(form.instance, related_orm_path, self.get_related_objects()[related_model_name])

        return form

    def perform_create(self, serializer):
        kwargs = {}

        for related_model_name in self.get_related_model_names():

            related_orm_path = self.get_related_orm_path(related_model_name)

            if "__" in related_orm_path:
                continue

            kwargs[related_orm_path] = self.get_related_objects()[related_model_name]

        serializer.save(**kwargs)


class RelatedObjectLimit:
    related_orm_path = None

    def get_queryset(self):
        queryset = super().get_queryset()

        related_orm_path = self.get_related_orm_path()
        related_object = self.get_related_object()

        return queryset.filter(**{related_orm_path: related_object})

    def get_related_orm_path(self):
        assert self.related_orm_path, f"{self.__class__.__name__} must define self.related_orm_path"
        return self.related_orm_path
    
    def get_related_object(self):
        raise NotImplementedError(f"{self.__class__.__name__} must implement self.get_related_object()")


class OrganizationLimit(auth_mixins.LoginRequiredMixin):
    organization_user_attribute = "organization"
    organization_orm_path = "organization"
    
    def get_queryset(self):
        q = super().get_queryset()
        org_orm_path = self.get_organization_orm_path()
        organization = self.get_organization()
        f = {org_orm_path: organization}
        return q.filter(**f)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.instance.organization = self.get_organization()
        return form

    def get_organization(self):
        return getattr(self.request.user, self.organization_user_attribute)

    def get_organization_orm_path(self):
        return self.organization_orm_path


class SoftDelete:
    
    def get_queryset(self):
        q = super().get_queryset()
        return q.filter(deleted=False)
