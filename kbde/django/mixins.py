from django.contrib.auth import mixins as auth_mixins
from django.contrib.staticfiles import finders
from django.templatetags import static


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
    related_queryset = None
    related_orm_path = None
    related_slug_field = "slug"
    related_slug_url_kwarg = "related_slug"
    related_pk_url_kwarg = "related_pk"

    def get_queryset(self):
        queryset = super().get_queryset()

        related_orm_path = self.get_related_orm_path()
        related_object = self.get_related_object()

        return queryset.filter(**{related_orm_path: related_object})

    def get_related_orm_path(self):
        assert self.related_orm_path, f"{self.__class__.__name__} must define `.related_orm_path`"
        return self.related_orm_path

    def get_related_object(self, related_queryset=None):
        if related_queryset is None:
            related_queryset = self.get_related_queryset()

        related_pk = self.kwargs.get(self.related_pk_url_kwarg)
        related_slug = self.kwargs.get(self.related_slug_url_kwarg)

        assert related_pk is not None or related_slug is not None, (f"{self.__class__.__name__} must "
                                                                     "be called with either a related "
                                                                     "pk or a slug in the URLconf")

        if related_pk is not None:
            # Filter by pk
            related_queryset = related_queryset.filter(pk=related_pk)
        else:
            # Filter by slug
            related_queryset = related_queryset.filter(**{self.related_slug_field: related_slug})

        try:
            obj = related_queryset.get()
        except related_queryset.model.DoesNotExist:
            raise http.Http404(f"No related {queryset.model._meta.verbose_name}s found matching the query")

        return obj

    def get_related_queryset(self):
        assert self.related_model is not None or self.related_queryset is not None, (""
                    f"{self.__class__.__name__} must define `.related_model` or .related_queryset")

        if self.related_queryset is not None:
            return self.related_queryset
        else:
            return self.related_model.objects.all()


class RelatedObjectForm(RelatedObject):
    
    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        if hasattr(form, "instance"):
            setattr(form.instance, self.related_orm_path, self.get_related_object())

        return form


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
