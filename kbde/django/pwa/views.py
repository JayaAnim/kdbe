from kbde.django import views as kbde_views
from kbde.django.json_views import views as json_views

from . import manifest


class Manifest(json_views.JsonView):
    
    def get_response_context(self, context):
        manifest_instance = manifest.Manifest.from_settings()
        return manifest_instance.to_dict()


class ServiceWorker(kbde_views.TemplateView):
    page_template_name = "kbde/django/pwa/views/ServiceWorker.js"
    permission_classes = []
    content_type = "text/javascript"
