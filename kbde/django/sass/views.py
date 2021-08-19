from django.core import management
from django.conf import settings
from kbde.django import views as kbde_views

from . import response


class Page(kbde_views.TemplateView):
    response_class = response.SassResponse
    permission_classes = []
    content_type = "text/css"

    def get(self, *args, **kwargs):
        if settings.DEBUG_SASS:
            management.call_command("collectstatic", "--no-input")

        return super().get(*args, **kwargs)

    def get_template_names(self):
        return [
            "sass/page.sass",
            "sass/page.scss",
        ]
