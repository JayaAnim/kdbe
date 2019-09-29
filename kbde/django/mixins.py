from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import mixins as auth_mixins
from django.contrib.staticfiles import finders
from django.templatetags import static

import pytz


class Base:
    template_name = "kbde/page.html"
    title = None
    icon = None
    bootstrap_css_path = "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.1/css/bootstrap.min.css"
    bootstrap_js_path = "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.1/js/bootstrap.min.js"
    jquery_path = "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"
    cookies_js_path = "https://cdnjs.cloudflare.com/ajax/libs/Cookies.js/1.2.1/cookies.min.js"
    css_list = []
    js_list = []
    open_graph = {}
    tracking_ids = []

    def dispatch(self, *args, **kwargs):
        self.set_timezone()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["icon"] = self.icon
        context["css_list"] = self.get_css_list()
        context["js_list"] = self.get_js_list()
        context["tracking_ids"] = ["UA-89983744-1"] + self.tracking_ids
        context["html_validate_forms"] = getattr(settings, "HTML_VALIDATE_FORMS", False)
        context["open_graph"] = self.get_open_graph()
        return context

    def set_timezone(self):
        tz = self.request.COOKIES.get("kb_tz")
        if tz:
            try:
                timezone.activate(tz)
            except pytz.UnknownTimeZoneError:
                pass
        else:
            timezone.deactivate()

    def get_css_list(self):
        css_list = [self.bootstrap_css_path]
        css_list += self.css_list
        return css_list

    def get_js_list(self):
        js_list = [
            self.jquery_path,
            self.bootstrap_js_path,
            self.cookies_js_path,
            ]
        js_list += self.js_list
        return js_list

    def get_open_graph(self):
        open_graph = self.open_graph.copy()

        for prop, content in open_graph.items():
            open_graph[prop] = self.get_static_url(content)

        return open_graph

    def get_static_url(self, path):
        if finders.find(path):
            path = static.static(path)
        return path


class Edit:
    success_message = None
    success_message_method = messages.info

    def get_success_url(self):
        success_message = self.get_success_message()
        if success_message is not None:
           type(self).success_message_method(self.request, success_message)

        return super().get_success_url()

    def get_success_message(self):
        return self.success_message


class EmailForm:
    
    def form_valid(self, form):
        # Send the email via the form
        form.send_email()
        return super().form_valid(form)


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
