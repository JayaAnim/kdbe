from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import mixins as auth_mixins
from django.contrib.staticfiles import finders
from django.templatetags import static

import pytz


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
