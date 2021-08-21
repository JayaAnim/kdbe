from django import http
from django.utils import decorators
from django.views.decorators import cache
from kbde.django import views as kbde_views

from . import sass


class Page(kbde_views.View):
    permission_classes = []

    @decorators.method_decorator(
        cache.cache_control(max_age=60*60*24*365)
    )
    def get(self, *args, **kwargs):
        return http.HttpResponse(
            sass.SassCompiler().get_css(self.request.GET),
            content_type="text/css",
        )
