from kbde.django import views as kbde_views
from kbde.django.json_views import views as json_views

from . import manifest


class ManifestMixin:
    manifest_class = manifest.Manifest

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        manifest = self.get_manifest()

        context_data.update({
            "manifest": manifest.to_dict()
        })

        return context_data

    def get_manifest(self):
        manifest_class = self.get_manifest_class()

        manifest = manifest_class.from_settings()

        return manifest

    def get_manifest_class(self):
        return self.manifest_class


class Manifest(ManifestMixin, json_views.JsonView):
    permission_classes = []
    content_type = "application/manifest+json"
    
    def get_response_context(self, context):
        return context["manifest"]


class ServiceWorker(ManifestMixin, kbde_views.TemplateView):
    page_template_name = "kbde/django/pwa/views/ServiceWorker.js"
    permission_classes = []
    content_type = "text/javascript"
