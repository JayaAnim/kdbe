from . import views


app_name = "pwa"

urlpatterns = [
    views.Manifest.get_urls_path("manifest.json"),
    views.ServiceWorker.get_urls_path("pwa_service_worker.js"),
]
