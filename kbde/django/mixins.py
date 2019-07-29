from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles import finders
from django.templatetags import static
from pytz import UnknownTimeZoneError


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

    def get_context_data(self, **kwargs):
        self.set_timezone()
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
            except UnknownTimeZoneError:
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
        if self.success_message is not None:
           type(self).success_message_method(self.request, self.success_message)
        return super().get_success_url()


class EmailForm:
    
    def form_valid(self, form):
        # Send the email via the form
        form.send_email()
        return super().form_valid(form)
