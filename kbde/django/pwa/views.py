from django.contrib.staticfiles import (
    utils as static_utils,
    storage as static_storage,
)
from django.templatetags import static
from kbde.django import views as kbde_views
from kbde.django.json_views import views as json_views

from . import manifest

import json


class Manifest(json_views.JsonView):
    
    def get_response_context(self, context):
        manifest_instance = manifest.Manifest.from_settings()
        return manifest_instance.to_dict()


class ServiceWorker(kbde_views.TemplateView):
    page_template_name = "kbde/django/pwa/views/ServiceWorker.js"
    permission_classes = []
    content_type = "text/javascript"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data["cache_paths_json"] = self.get_cache_paths_json()

        return context_data

    def get_cache_paths_json(self):
        return json.dumps(self.get_cache_paths())

    def get_cache_paths(self):
        storage = static_storage.StaticFilesStorage()
        file_paths = static_utils.get_files(storage)

        return [static.static(path) for path in file_paths]
