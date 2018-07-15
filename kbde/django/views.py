from django.views.generic import TemplateView
from django.utils import timezone
from pytz import UnknownTimeZoneError


class BaseView(TemplateView):
    title = None
    icon = None
    bootstrap_css_path = "https://cdnjs.cloudflare.com/ajax/libs/bootswatch/4.1.1/materia/bootstrap.css"
    bootstrap_js_path = "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.1/js/bootstrap.min.js"
    jquery_path = "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"

    def get_context_data(self, **kwargs):
        self.set_timezone()
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["user"] = self.request.user
        context["url_name"] = self.request.resolver_match.url_name
        context["icon"] = self.icon
        context["css_list"] = self.get_css_list()
        context["js_list"] = self.get_js_list()
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
        return [self.bootstrap_css_path]

    def get_js_list(self):
        return [self.jquery_path, self.bootstrap_js_path]
